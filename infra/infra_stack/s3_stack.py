from aws_cdk import (
    aws_s3 as s3,
    Stack,
    RemovalPolicy,
)
from constructs import Construct

class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        self.bucket = s3.Bucket(self, "SanctionsDataBucket",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY
        )
