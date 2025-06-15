import os
import json
import time
import requests
from slack_sdk import WebClient
import boto3
import csv
import io

# Config
BUCKET = os.environ["S3_BUCKET"]
KEY = os.environ["S3_KEY"]
SLACK_TOKEN = os.environ["SLACK_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

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
    # Compare by 'id' and 'name'
    old_set = set((entry["id"], entry["name"]) for entry in old)
    new_set = set((entry["id"], entry["name"]) for entry in new)
    added = [entry for entry in new if (entry["id"], entry["name"]) not in old_set]
    removed = [entry for entry in old if (entry["id"], entry["name"]) not in new_set]
    return {"added": added, "removed": removed}

def notify_slack(records, delta, duration):
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

def handler(event, context):
    start = time.time()

    csv_text = fetch_sanctions()
    current_list = parse_csv_to_json(csv_text)
    previous_list = load_previous_list()

    delta = compare_lists(previous_list, current_list)

    save_to_s3_json(current_list)

    duration = time.time() - start

    notify_slack(len(current_list), delta, duration)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "added": len(delta["added"]),
            "removed": len(delta["removed"]),
            "duration": duration
        })
    }