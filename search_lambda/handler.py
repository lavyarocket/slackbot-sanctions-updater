import os
import json
import urllib.parse
import boto3
import requests

SDN_BUCKET = os.environ.get("SDN_BUCKET")  # Set in Lambda environment
SDN_KEY = os.environ.get("SDN_KEY")        # Set in Lambda environment

def load_sdn_list():
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=SDN_BUCKET, Key=SDN_KEY)
    data = obj["Body"].read().decode("utf-8")
    return json.loads(data)

def search_sdn(name, sdn_list):
    name = name.lower()
    return [entry for entry in sdn_list if "name" in entry and name in entry["name"].lower()]

def format_slack_blocks(results, query):
    if not results:
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":white_check_mark: No SDN records found for *{query}*."
                }
            }
        ]
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":warning: *Found {len(results)} SDN record(s) for* `{query}`:"
            }
        }
    ]
    for entry in results[:10]:  # Limit to 10 results for readability
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Name:* {entry.get('name')}\n"
                    f"*ID:* {entry.get('id', 'N/A')}\n"
                    f"*Type:* {entry.get('type', 'N/A')}\n"
                    f"*Program:* {entry.get('program', 'N/A')}"
                )
            }
        })
        blocks.append({"type": "divider"})
    return blocks

def handler(event, context):
    query = event["query"]
    response_url = event["response_url"]

    sdn_list = load_sdn_list()
    results = search_sdn(query, sdn_list)
    blocks = format_slack_blocks(results, query)

    requests.post(response_url, json={
        "response_type": "in_channel" if results else "ephemeral",
        "blocks": blocks
    })

    return {"status": "posted to slack"}