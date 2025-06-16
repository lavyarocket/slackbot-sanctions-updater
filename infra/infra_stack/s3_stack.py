from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
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
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[f"{self.bucket.bucket_arn}/*"],
                principals=[iam.ArnPrincipal("*")],
                effect=iam.Effect.ALLOW
            )
        )
