import os
import json
import boto3
import urllib.parse

sfn = boto3.client("stepfunctions")

def handler(event, context):
    # Slack sends x-www-form-urlencoded data
    body = event.get("body", "")
    params = urllib.parse.parse_qs(body)
    text = params.get("text", [""])[0].strip()
    response_url = params.get("response_url", [""])[0]

    if not text or not response_url:
        return {
            "statusCode": 200,
            "body": json.dumps({
            "response_type": "ephemeral",
            "text": "Please provide a name to check. Usage: /check_sdn <name>"
        })
        }

    # Start Step Function with query and response_url
    sfn.start_execution(
        stateMachineArn=os.environ["STATE_MACHINE_ARN"],
        input=json.dumps({
            "query": text,
            "response_url": response_url
        })
    )

    # Immediate response to Slack
    return {
        "statusCode": 200,
        "body": json.dumps({
            "response_type": "ephemeral",
            "text": f"Looking up `{text}` in the SDN list... please wait."
        })
    }
