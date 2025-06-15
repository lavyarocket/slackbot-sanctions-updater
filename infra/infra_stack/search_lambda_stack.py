from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_apigateway as apigw,
    aws_iam as iam,
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

        # API Gateway endpoint for Slack slash command
        api = apigw.RestApi(self, "CheckSdnApi",
            rest_api_name="Check SDN Service",
            description="Slack /check_sdn command endpoint."
        )

        check_sdn_resource = api.root.add_resource("check_sdn")
        check_sdn_resource.add_method(
            "POST",
            apigw.LambdaIntegration(self.lambda_fn)
        )