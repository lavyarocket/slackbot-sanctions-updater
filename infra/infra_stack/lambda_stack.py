from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct
import os
from aws_cdk.aws_lambda_python_alpha import PythonFunction

class LambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, s3_bucket: s3.IBucket, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.lambda_fn = _lambda.DockerImageFunction(
        self, "SDNSyncFunction",
        code=_lambda.DockerImageCode.from_image_asset(
            os.path.join(os.path.dirname(__file__), "../../lambda")
        ),
        environment={
            "S3_BUCKET": s3_bucket.bucket_name,
            "S3_KEY": "sdn/latest.json",
            "SLACK_TOKEN": "xoxb-9049134471330-9062064648913-gqGHPC7ko3AdUKDIn2pw2nHH",
            "SLACK_CHANNEL": "#alerts"
        },
        timeout=Duration.minutes(5),
        )
       
        # Grant permissions
        s3_bucket.grant_read_write(self.lambda_fn)

        # Optional: Add IAM policy for Slack, if needed
        self.lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["secretsmanager:GetSecretValue"],
            resources=["*"]
        ))

        # EventBridge trigger
        rule = events.Rule(self, "DailySDNTrigger",
            schedule=events.Schedule.cron(minute="0", hour="15")  # UTC
        )
        rule.add_target(targets.LambdaFunction(self.lambda_fn))
