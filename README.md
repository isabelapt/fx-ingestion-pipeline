# FX Ingestion Pipeline: AWS IAM Roles & Permissions Guide

This guide details the IAM Roles and permissions required to deploy and run the **FX Ingestion Pipeline** infrastructure using Terraform and GitHub Actions.

---

## 1. Deployment Role: `GitHubActionsFXPipelineRole`

This role is assumed by GitHub Actions via OIDC (`aws-actions/configure-aws-credentials`) to run Terraform (`terraform plan` and `terraform apply`).

### Required Permissions & Why They Are Necessary

Terraform works by comparing the local configuration against the real resources deployed in AWS. Therefore, this role requires permissions to **Create, Read (List/Get), Update, Delete, and Tag** all resources defined in our HCL files.

| Service | Action Categories | Specific Actions Required | Why It's Necessary |
| :--- | :--- | :--- | :--- |
| **S3** | Read / Write | `s3:CreateBucket`, `s3:ListBucket`, `s3:GetBucketNotification`, `s3:PutBucketNotification` | To read/write the Terraform state file in the remote backend and configure EventBridge notifications on the raw data bucket. |
| **IAM** | Manage Lambda Role | `iam:CreateRole`, `iam:GetRole`, `iam:DeleteRole`, `iam:PassRole`, `iam:ListRolePolicies`, `iam:ListAttachedRolePolicies`, `iam:GetRolePolicy`, `iam:PutRolePolicy`, `iam:DeleteRolePolicy` | To create and manage the execution role for the Lambda function and attach policy bindings. |
| **Lambda** | Function Management | `lambda:CreateFunction`, `lambda:GetFunction`, `lambda:DeleteFunction`, `lambda:UpdateFunctionCode`, `lambda:UpdateFunctionConfiguration`, `lambda:AddPermission`, `lambda:RemovePermission`, `lambda:TagResource`, `lambda:ListVersionsByFunction`, `lambda:GetFunctionEventInvokeConfig`, `lambda:PutFunctionEventInvokeConfig` | To deploy the ingestion Lambda ZIP package, configure environment variables, tag the resource, list versions, configure async retries, and allow EventBridge invocation. |
| **EventBridge** | Rule & Target Management | `events:PutRule`, `events:DescribeRule`, `events:DeleteRule`, `events:PutTargets`, `events:RemoveTargets`, `events:ListTargetsByRule` | To capture S3 upload events and schedule the daily CRON trigger, routing them to SNS/Lambda. |
| **SNS** | Alerting | `sns:CreateTopic`, `sns:GetTopicAttributes`, `sns:SetTopicAttributes`, `sns:DeleteTopic`, `sns:Publish` | To configure alerting channels for successful ingestions and failure alarms. |
| **Glue** | Data Catalog | `glue:CreateDatabase`, `glue:GetDatabase`, `glue:DeleteDatabase`, `glue:TagResource`, `glue:GetTags` | To catalog the raw S3 partitions so Athena can query exchange rates. |
| **CloudWatch** | Alarms & Monitoring | `cloudwatch:PutMetricAlarm`, `cloudwatch:DescribeAlarms`, `cloudwatch:DeleteAlarms` | To create and manage the error metric alarms for the Lambda function. |

### Minimal Inline Policy JSON for Deployment Role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "lambda:*",
        "events:*",
        "sns:*",
        "glue:*",
        "cloudwatch:*",
        "iam:CreateRole",
        "iam:GetRole",
        "iam:DeleteRole",
        "iam:PassRole",
        "iam:ListRolePolicies",
        "iam:ListAttachedRolePolicies",
        "iam:GetRolePolicy",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:GetPolicyVersion"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 2. Ingestion Execution Role: `fx-ingestion-lambda-role-<env>`

This role is assumed by the AWS Lambda function at runtime.

### Required Permissions & Why They Are Necessary

| Policy / Permission | Actions | Why It's Necessary |
| :--- | :--- | :--- |
| **`AWSLambdaBasicExecutionRole`** (Managed) | `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` | Allows the function to write its execution logs to AWS CloudWatch for debugging and tracking. |
| **S3 Least-Privilege Policy** | `s3:PutObject`, `s3:GetObject`, `s3:ListBucket` | Allows the python ingestion code to fetch Frankfurter API payloads and upload them to the S3 raw storage partition. |

### Terraform Resource Configuration

This role and its permissions are declared declaratively in [main.tf](file:///c:/Users/isabe/Documents/projetos/fx-ingestion-pipeline/infra/terraform/main.tf):

```hcl
resource "aws_iam_role" "lambda_exec_role" {
  name = local.lambda_role_name
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = local.lambda_s3_policy_name
  description = "Allows Lambda to write raw FX rate payloads into S3 bucket"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:PutObject", "s3:GetObject", "s3:ListBucket"]
      Resource = [
        data.aws_s3_bucket.fx_raw_data.arn,
        "${data.aws_s3_bucket.fx_raw_data.arn}/*"
      ]
    }]
  })
}
```
