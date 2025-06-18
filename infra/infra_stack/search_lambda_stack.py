from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_apigateway as apigw,
    aws_iam as iam,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks
)
from constructs import Construct
import os

class CheckSdnStack(Stack):
    def __init__(self, scope: Construct, id: str, s3_bucket: s3.IBucket, **kwargs):
        super().__init__(scope, id, **kwargs)


        self.lambda_fn = _lambda.DockerImageFunction(
            self, "CheckSdnLambda",
            code=_lambda.DockerImageCode.from_image_asset(
            os.path.join(os.path.dirname(__file__), "../../search_lambda")
            ),
            environment={
            "SDN_BUCKET": s3_bucket.bucket_name,
            "SDN_KEY": "sdn/latest.json",
            },
            timeout=Duration.minutes(5),
        )

        # Grant permissions to the Lambda function to read from the S3 bucket
        s3_bucket.grant_read_write(self.lambda_fn)

        step_task = tasks.LambdaInvoke(
            self, "InvokeCheckSdnLambda",
            lambda_function=self.lambda_fn,
            output_path="$.Payload"
        )

        state_machine = sfn.StateMachine(
            self, "CheckSdnStateMachine",
            definition_body=sfn.DefinitionBody.from_chainable(step_task),
            timeout=Duration.minutes(10)
        )

        trigger_lambda = _lambda.Function(
            self, "TriggerCheckSdnWorkflow",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="trigger_lambda.handler",
            code=_lambda.Code.from_asset(
            os.path.join(os.path.dirname(__file__), "../../search_lambda")
            ),
            environment={
                "STATE_MACHINE_ARN": state_machine.state_machine_arn
            },
            timeout=Duration.seconds(10),
        )
        state_machine.grant_start_execution(trigger_lambda)


        # API Gateway endpoint for Slack slash command
        api = apigw.RestApi(self, "CheckSdnApi",
            rest_api_name="Check SDN Service",
            description="Slack /check_sdn command endpoint."
        )

        check_sdn_resource = api.root.add_resource("check_sdn")
        check_sdn_resource.add_method(
            "POST",
            apigw.LambdaIntegration(trigger_lambda)
        )