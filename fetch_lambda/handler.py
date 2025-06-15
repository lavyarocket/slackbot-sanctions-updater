import os
import json
import time
import requests
from slack_sdk import WebClient
import boto3

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
    return resp.text.splitlines()

def load_previous_list():
    try:
        response = S3.get_object(Bucket=BUCKET, Key=KEY)
        return response["Body"].read().decode("utf-8").splitlines()
    except S3.exceptions.NoSuchKey:
        return []

def save_to_s3(data):
    S3.put_object(Bucket=BUCKET, Key=KEY, Body="\n".join(data))

def compare_lists(old, new):
    added = [line for line in new if line not in old]
    removed = [line for line in old if line not in new]
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

    current_list = fetch_sanctions()
    previous_list = load_previous_list()

    delta = compare_lists(previous_list, current_list)

    save_to_s3(current_list)

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
