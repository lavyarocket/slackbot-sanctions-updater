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
        self.bucket.add_to_resource_policy(
            s3.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[f"{self.bucket.bucket_arn}/*"],
                principals=[s3.ArnPrincipal("*")],
                effect=s3.Effect.ALLOW,
                conditions={
                    "StringEquals": {"s3:acl": "public-read"}
                }
            )
        )
