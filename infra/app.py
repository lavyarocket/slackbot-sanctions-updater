#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from infra_stack.s3_stack import S3Stack
from infra_stack.fetch_lambda_stack import LambdaStack
from infra_stack.search_lambda_stack import CheckSdnStack

app = App()

env = Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region="us-east-1")

s3_stack = S3Stack(app, "SanctionsS3Stack", env=env)
fetch_lambda_stack = LambdaStack(app, "Fetch_SanctionsLambdaStack", s3_bucket=s3_stack.bucket, env=env)
search_lambda_stack = CheckSdnStack(app, "Search_SanctionsLambdaStack", s3_bucket=s3_stack.bucket, env=env)

app.synth()
