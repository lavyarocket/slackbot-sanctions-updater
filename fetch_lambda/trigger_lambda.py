# trigger_lambda.py
import os
import json
import boto3

SFN = boto3.client("stepfunctions")

def handler(event, context):
    try:
        response = SFN.start_execution(
            stateMachineArn=os.environ["STATE_MACHINE_ARN"],
            input=json.dumps(event)
        )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "response_type": "ephemeral",
                "text": "Sanctions update started. Results will be posted here shortly."
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
