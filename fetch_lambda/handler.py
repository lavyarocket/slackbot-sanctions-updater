import os
import json
import time
import requests
from slack_sdk import WebClient
import boto3
import csv
import io
import matplotlib.pyplot as plt
from datetime import datetime


BUCKET = os.environ["S3_BUCKET"]
KEY = os.environ["S3_KEY"]
SLACK_TOKEN = os.environ["SLACK_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]
SANCTIONS_HISTORY_KEY = os.environ.get("SANCTIONS_HISTORY_KEY", "sdn/sanctions_history.json")
SANCTIONS_DIFFS_KEY = os.environ.get("SANCTIONS_DIFFS_KEY", "sdn/sanctions_diffs.json")

S3 = boto3.client("s3")
SLACK = WebClient(token=SLACK_TOKEN)

def fetch_sanctions():
    url = "https://www.treasury.gov/ofac/downloads/sdn.csv"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def parse_csv_to_json(csv_text):
    reader = csv.reader(io.StringIO(csv_text))
    sdn_list = []
    for row in reader:
        if len(row) < 4:
            continue
        sdn_list.append({
            "id": row[0],
            "name": row[1].strip('"'),
            "type": row[2].strip('"'),
            "program": row[3].strip('"'),
        })
    return sdn_list

def load_previous_list():
    try:
        response = S3.get_object(Bucket=BUCKET, Key=KEY)
        data = response["Body"].read().decode("utf-8")
        return json.loads(data)
    except S3.exceptions.NoSuchKey:
        return []

def save_to_s3_json(data):
    S3.put_object(Bucket=BUCKET, Key=KEY, Body=json.dumps(data, indent=2), ContentType="application/json")

def compare_lists(old, new):
    old_set = set((entry["id"], entry["name"]) for entry in old)
    new_set = set((entry["id"], entry["name"]) for entry in new)
    added = [entry for entry in new if (entry["id"], entry["name"]) not in old_set]
    removed = [entry for entry in old if (entry["id"], entry["name"]) not in new_set]
    return {"added": added, "removed": removed}



def notify_slack(records, delta, duration, chart_buf=None):
    url = S3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": KEY},
        ExpiresIn=86400
    )

    text = (
        f"*🛡 Daily Sanctions Update*\n"
        f"> *Total Records:* {records}\n"
        f"> *➕ New:* {len(delta['added'])}  |  *➖ Removed:* {len(delta['removed'])}\n"
        f"> *Run Time:* `{duration:.2f}`s\n"
        f"<{url}|📄 View latest list>"
    )
    SLACK.chat_postMessage(channel=SLACK_CHANNEL, text=text)

    if chart_buf:
        chart_key = f"sdn/sanctions_changes_{int(time.time())}.png"
        chart_buf.seek(0)
        # Upload with public-read ACL
        S3.put_object(
            Bucket=BUCKET,
            Key=chart_key,
            Body=chart_buf,
            ContentType="image/png"
        )
        # Construct the public S3 URL
        chart_url = f"https://{BUCKET}.s3.amazonaws.com/{chart_key}"
        SLACK.chat_postMessage(
            channel=SLACK_CHANNEL,
            blocks=[
                {
                    "type": "image",
                    "image_url": chart_url,
                    "alt_text": "Sanctions List Changes (Last 7 Lookups)"
                }
            ],
            text="Sanctions list changes over the last 7 lookups."
        )



def load_json_from_s3(key):
    try:
        obj = S3.get_object(Bucket=BUCKET, Key=key)
        return json.loads(obj['Body'].read())
    except S3.exceptions.NoSuchKey:
        return []
    except Exception as e:
        print(f"Error loading {key}: {e}")
        return []

def save_json_to_s3(data, key):
    S3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(data).encode("utf-8"))


def update_history_and_diffs(delta):

    diffs = load_json_from_s3(SANCTIONS_DIFFS_KEY)
    # Compute additions and deletions
    additions, deletions = len(delta["added"]), len(delta["removed"])


    # Store only counts for charting
    diffs.append({
        "timestamp": datetime.utcnow().isoformat(),
        "additions_count": additions,
        "deletions_count": deletions
    })
    diffs = diffs[-7:]
    
    save_json_to_s3(diffs, SANCTIONS_DIFFS_KEY)

    return diffs

def generate_chart(diffs):
    # Always show last 7 lookups, even if some are empty
    dates = [(d['timestamp'][:16] if 'timestamp' in d else '') for d in diffs]
    additions = [d.get('additions_count', 0) for d in diffs]
    deletions = [d.get('deletions_count', 0) for d in diffs]

    plt.figure(figsize=(10, 5))
    x = range(len(dates))
    width = 0.35

    plt.bar([i - width/2 for i in x], additions, width=width, color='green', label='Additions')
    plt.bar([i + width/2 for i in x], deletions, width=width, color='red', label='Deletions')
    plt.xticks(x, dates, rotation=30, ha='right')
    plt.xlabel('Date & Time (UTC)')
    plt.ylabel('Count')
    plt.title('Sanctions List Changes (Last 7 Lookups)')
    plt.legend()
    plt.tight_layout()
    plt.ylim(bottom=0)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

def handler(event, context):
    start = time.time()

    csv_text = fetch_sanctions()
    current_list = parse_csv_to_json(csv_text)
    previous_list = load_previous_list()

    delta = compare_lists(previous_list, current_list)

    save_to_s3_json(current_list)

    diffs = update_history_and_diffs(delta)
    chart_buf = generate_chart(diffs)
    duration = time.time() - start

    notify_slack(len(current_list), delta, duration, chart_buf=chart_buf)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "added": len(delta["added"]),
            "removed": len(delta["removed"]),
            "duration": duration,
            "message": "Sanctions update processed and chart sent to Slack."
        })
    }