# Infra Folder

This folder contains the AWS CDK (Cloud Development Kit) code that defines and deploys all infrastructure for the Slackbot Sanctions Updater project.

## Stacks Overview

- **Fetch Lambda Stack**: Provisions the Lambda function, IAM roles, and scheduling resources for downloading and processing the OFAC SDN list.
- **Search Lambda Stack**: Provisions the Lambda function, API Gateway, and Step Function for handling Slack slash command requests and searching the SDN list.
- **S3 Bucket Stack**: Creates the S3 bucket used to store the latest and historical SDN data.
- **Secrets Manager Integration**: Grants Lambda functions permission to securely retrieve the Slack bot token from AWS Secrets Manager.

## Structure

- `infra_stack/`: Contains the CDK stack definitions for each component.
- `app.py`: Entry point for the CDK application.

## Usage

To deploy or update the infrastructure, use the CDK CLI from this directory:

```sh
cd infra
pip install -r requirements.txt
cdk deploy
```

For more details on CDK commands, see the [AWS CDK documentation](https://docs.aws.amazon.com/cdk/latest/guide/cli.html).