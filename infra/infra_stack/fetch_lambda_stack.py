from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks
)
from constructs import Construct
import os
from aws_cdk.aws_lambda_python_alpha import PythonFunction
import boto3
from botocore.exceptions import ClientError
from aws_cdk import aws_apigateway as apigateway

class LambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, s3_bucket: s3.IBucket, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Use environment variable for SLACK_TOKEN, fallback to empty string if not set
        def get_secret():

            secret_name = "sanctions-bot-slack-token"
            region_name = "us-east-1"

            # Create a Secrets Manager client
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=region_name
            )

            try:
                get_secret_value_response = client.get_secret_value(
                    SecretId=secret_name
                )
            except ClientError as e:
                # For a list of exceptions thrown, see
                # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
                raise e

            return get_secret_value_response['SecretString']


        self.lambda_fn = _lambda.DockerImageFunction(
            self, "SDNSyncFunction",
            code=_lambda.DockerImageCode.from_image_asset(
            os.path.join(os.path.dirname(__file__), "../../fetch_lambda")
            ),
            environment={
            "S3_BUCKET": s3_bucket.bucket_name,
            "S3_KEY": "sdn/latest.json",
            "SLACK_TOKEN": get_secret(),
            "SLACK_CHANNEL": "#alerts"
            },
            timeout=Duration.minutes(5),
            memory_size=512,
        )
        # Grant permissions
        s3_bucket.grant_read_write(self.lambda_fn)

        # Optional: Add IAM policy for Slack, if needed
        self.lambda_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["secretsmanager:GetSecretValue"],
            resources=["*"]
        ))

        step_task = tasks.LambdaInvoke(
            self, "InvokeSanctionsLambda",
            lambda_function=self.lambda_fn,
            output_path="$.Payload"
        )

        state_machine = sfn.StateMachine(
            self, "SanctionsStepFunction",
            definition=step_task,
            timeout=Duration.minutes(10)
        )

        trigger_lambda = _lambda.Function(
            self, "TriggerSanctionsWorkflow",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="trigger_lambda.handler",
            code=_lambda.Code.from_asset("../../fetch_lambda"),
            environment={
                "STATE_MACHINE_ARN": state_machine.state_machine_arn
            },
            timeout=Duration.seconds(10),
        )
        state_machine.grant_start_execution(trigger_lambda)

        # EventBridge trigger: run at 8am, 4pm, and 11pm PDT (which is 15, 23, and 6 UTC)
        rule = events.Rule(self, "ThreeTimesDailySDNTrigger",
            schedule=events.Schedule.cron(minute="0", hour="15,23,6")  # UTC times
        )
        rule.add_target(targets.LambdaFunction(self.lambda_fn))

        api = apigateway.RestApi(
            self, "SDNSyncApiGateway",
            rest_api_name="SDNSyncApi"
        )

        trigger_resource = api.root.add_resource("trigger")
        trigger_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(trigger_lambda)
        )
        