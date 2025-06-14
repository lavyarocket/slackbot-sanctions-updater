#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from infra_stack.s3_stack import S3Stack
from infra_stack.lambda_stack import LambdaStack

app = App()

env = Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region="us-east-1")

s3_stack = S3Stack(app, "SanctionsS3Stack", env=env)
lambda_stack = LambdaStack(app, "SanctionsLambdaStack", s3_bucket=s3_stack.bucket, env=env)

app.synth()
