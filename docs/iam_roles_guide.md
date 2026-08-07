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

### Resource-Restricted Policy JSON for Deployment Role

```json
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "S3BucketAccess",
			"Effect": "Allow",
			"Action": [
				"s3:CreateBucket",
				"s3:DeleteBucket",
				"s3:GetBucketLocation",
				"s3:ListBucket",
				"s3:PutBucketLogging",
				"s3:PutBucketNotification",
				"s3:PutLifecycleConfiguration",
				"s3:GetLifecycleConfiguration",
				"s3:PutEncryptionConfiguration",
				"s3:GetEncryptionConfiguration",
				"s3:PutBucketPublicAccessBlock",
				"s3:GetBucketPublicAccessBlock",
				"s3:GetBucketNotification"
			],
			"Resource": [
				"arn:aws:s3:::fx-ingestion-raw-data-dev",
				"arn:aws:s3:::fx-ingestion-raw-data-dev/*"
			]
		},
		{
			"Sid": "LambdaFunctionAccess",
			"Effect": "Allow",
			"Action": [
				"lambda:CreateFunction",
				"lambda:GetFunction",
				"lambda:DeleteFunction",
				"lambda:UpdateFunctionCode",
				"lambda:UpdateFunctionConfiguration",
				"lambda:AddPermission",
				"lambda:RemovePermission",
				"lambda:TagResource",
				"lambda:ListVersionsByFunction",
				"lambda:GetFunctionCodeSigningConfig",
				"lambda:PutFunctionEventInvokeConfig",
				"lambda:GetFunctionEventInvokeConfig"
			],
			"Resource": "arn:aws:lambda:us-east-1:123456789012:function:fx-rate-ingestor-dev"
		},
		{
			"Sid": "CloudWatchAlarmsAccess",
			"Effect": "Allow",
			"Action": [
				"cloudwatch:PutMetricAlarm",
				"cloudwatch:DeleteAlarms"
			],
			"Resource": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:fx-ingestor-error-alarm-dev"
		},
		{
			"Sid": "CloudWatchDescribeAlarms",
			"Effect": "Allow",
			"Action": [
				"cloudwatch:DescribeAlarms"
			],
			"Resource": "*"
		},
		{
			"Sid": "EventBridgeRulesAccess",
			"Effect": "Allow",
			"Action": [
				"events:PutRule",
				"events:DescribeRule",
				"events:DeleteRule",
				"events:PutTargets",
				"events:RemoveTargets",
				"events:ListTargetsByRule",
				"events:ListTagsForResource",
				"events:TagResource"
			],
			"Resource": [
				"arn:aws:events:us-east-1:123456789012:rule/fx-ingestion-daily-cron-dev",
				"arn:aws:events:us-east-1:123456789012:rule/fx-s3-raw-upload-rule-dev"
			]
		},
		{
			"Sid": "SNSTopicsAccess",
			"Effect": "Allow",
			"Action": [
				"sns:CreateTopic",
				"sns:GetTopicAttributes",
				"sns:SetTopicAttributes",
				"sns:DeleteTopic",
				"sns:ListTagsForResource",
				"sns:TagResource"
			],
			"Resource": [
				"arn:aws:sns:us-east-1:123456789012:fx-ingestion-alerts-topic-dev",
				"arn:aws:sns:us-east-1:123456789012:fx-ingestion-data-ready-topic-dev"
			]
		},
		{
			"Sid": "GlueDatabaseAccess",
			"Effect": "Allow",
			"Action": [
				"glue:CreateDatabase",
				"glue:GetDatabase",
				"glue:UpdateDatabase",
				"glue:DeleteDatabase",
				"glue:TagResource",
				"glue:GetTags"
			],
			"Resource": [
				"arn:aws:glue:us-east-1:123456789012:catalog",
				"arn:aws:glue:us-east-1:123456789012:database/fx_rates_db_dev"
			]
		},
		{
			"Sid": "IAMExecutionRoleAccess",
			"Effect": "Allow",
			"Action": [
				"iam:CreateRole",
				"iam:GetRole",
				"iam:DeleteRole",
				"iam:TagRole",
				"iam:AttachRolePolicy",
				"iam:DetachRolePolicy",
				"iam:PassRole",
				"iam:ListRolePolicies",
				"iam:ListAttachedRolePolicies"
			],
			"Resource": "arn:aws:iam::123456789012:role/fx-ingestion-lambda-role-dev"
		},
		{
			"Sid": "IAMPolicyAccess",
			"Effect": "Allow",
			"Action": [
				"iam:CreatePolicy",
				"iam:GetPolicy",
				"iam:DeletePolicy",
				"iam:ListPolicyVersions",
				"iam:CreatePolicyVersion",
				"iam:DeletePolicyVersion",
				"iam:GetPolicyVersion",
				"iam:TagPolicy"
			],
			"Resource": "arn:aws:iam::123456789012:policy/fx-lambda-s3-write-dev"
		}
	]
}
```

### Detailed Explanation of Each Action by Service

#### 🪣 Service: S3 (Resource: `fx-ingestion-raw-data-dev`)
* `s3:CreateBucket` / `s3:DeleteBucket`: Allows Terraform to provision and destroy the Data Lake storage bucket.
* `s3:ListBucket` / `s3:GetBucketLocation`: Allows Terraform to verify bucket existence and determine its geographical region.
* `s3:PutEncryptionConfiguration` / `s3:GetEncryptionConfiguration`: Enforces server-side encryption at rest for bucket data.
* `s3:PutBucketPublicAccessBlock` / `s3:GetBucketPublicAccessBlock`: Blocks all public write/read permissions to prevent data exposure.
* `s3:PutBucketNotification` / `s3:GetBucketNotification`: Configures native EventBridge integration notifications on S3 object creation.

#### ⚡ Service: Lambda (Resource: `fx-rate-ingestor-dev`)
* `lambda:CreateFunction` / `lambda:DeleteFunction`: Creates and deletes the runtime environment and properties of the ingestion function.
* `lambda:UpdateFunctionCode` / `lambda:UpdateFunctionConfiguration`: Deploys new ZIP builds and updates environment variables.
* `lambda:AddPermission` / `lambda:RemovePermission`: Allows associating external trigger permissions (like EventBridge rules) to the function.
* `lambda:GetFunctionCodeSigningConfig` / `lambda:ListVersionsByFunction`: Utilized by Terraform for codebase verification and lifecycle management.
* `lambda:PutFunctionEventInvokeConfig` / `lambda:GetFunctionEventInvokeConfig`: Configures asynchronous execution settings (number of retry attempts).

#### 🚨 Service: CloudWatch Alarms (Resource: `fx-ingestor-error-alarm-dev`)
* `cloudwatch:PutMetricAlarm` / `cloudwatch:DeleteAlarms`: Provisions and deletes the threshold metrics monitor.
* `cloudwatch:DescribeAlarms` (Resource: `*`): Inspects existing alarms during `terraform plan` execution (AWS requires global scope `*` for this read action).

#### 📨 Service: EventBridge Rules (Resource: `fx-ingestion-daily-cron-dev` and `fx-s3-raw-upload-rule-dev`)
* `events:PutRule` / `events:DeleteRule` / `events:DescribeRule`: Creates, updates, and deletes event triggers (CRON schedule and S3 upload listeners).
* `events:PutTargets` / `events:RemoveTargets` / `events:ListTargetsByRule`: Maps downstream targets (Lambda, SNS) to the event rules.

#### 📣 Service: SNS (Resource: topics `fx-ingestion-alerts-topic-dev` and `fx-ingestion-data-ready-topic-dev`)
* `sns:CreateTopic` / `sns:DeleteTopic`: Creates and deletes SNS topics.
* `sns:SetTopicAttributes` / `sns:GetTopicAttributes`: Allows updating topic access configurations (such as granting publish permissions to CloudWatch or EventBridge).

#### 🗄️ Service: Glue Catalog (Resource: `catalog` and `fx_rates_db_dev`)
* `glue:CreateDatabase` / `glue:GetDatabase` / `glue:UpdateDatabase` / `glue:DeleteDatabase`: Provisions and manages metadata databases in AWS Glue, allowing Athena to run SQL queries over the S3 bucket.

#### 🔑 Service: IAM (Resource: role `fx-ingestion-lambda-role-dev` and policy `fx-lambda-s3-write-dev`)
* `iam:CreateRole` / `iam:GetRole` / `iam:DeleteRole` / `iam:PassRole`: Manages the lifecycle of the execution role and passes it to the Lambda service.
* `iam:AttachRolePolicy` / `iam:DetachRolePolicy`: Associates or detaches policy documents (e.g. S3 write policy) to the Lambda role.
* `iam:CreatePolicy` / `iam:GetPolicy` / `iam:DeletePolicy` / `iam:CreatePolicyVersion`: Configures custom permission documents that grant S3 write/read privileges to the Lambda.

---

## 2. Ingestion Execution Role: `fx-ingestion-lambda-role-<env>`

This role is assumed by the AWS Lambda function at runtime.

### Required Permissions & Why They Are Necessary

| Policy / Permission | Actions | Why It's Necessary |
| :--- | :--- | :--- |
| **`AWSLambdaBasicExecutionRole`** (Managed) | `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` | Allows the function to write its execution logs to AWS CloudWatch for debugging and tracking. |
| **S3 Least-Privilege Policy** | `s3:PutObject`, `s3:GetObject`, `s3:ListBucket` | Allows the python ingestion code to fetch Frankfurter API payloads and upload them to the S3 raw storage partition. |

### Terraform Resource Configuration

This role and its permissions are declared declaratively in [main.tf](../infra/terraform/main.tf):

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

---

## 3. Infrastructure Architecture & Data Flows

The following diagram illustrates how the AWS resources deployed by Terraform connect with each other, defining the **Scheduled Ingestion Flow**, the **Error Handling Flow**, and the **Downstream Event Integration Flow**:

```mermaid
flowchart TB
    %% Nodes styling
    classDef aws fill:#232F3E,stroke:#FF9900,stroke-width:2px,color:white;
    classDef client fill:#1A73E8,stroke:#0F9D58,stroke-width:2px,color:white;
    classDef external fill:#7A7A7A,stroke:#333333,stroke-width:2px,color:white;
    
    subgraph Triggers ["Triggers & Events"]
        Cron["⏰ EventBridge Cron<br/>(daily_trigger)"]:::aws
        S3_Event["📨 EventBridge Rule<br/>(s3_raw_upload_rule)"]:::aws
    end

    subgraph Computing ["Compute & Logic"]
        Lambda["⚡ AWS Lambda<br/>(fx-rate-ingestor-dev)"]:::aws
    end

    subgraph StorageCatalog ["Storage & Metadata"]
        S3["🪣 S3 Raw Bucket<br/>(fx-ingestion-raw-data-dev)"]:::aws
        Glue["🗄️ Glue Catalog Database<br/>(fx_rates_db_dev)"]:::aws
    end

    subgraph Observers ["Monitoring & Alerts"]
        Alarm["🚨 CloudWatch Metric Alarm<br/>(lambda_error_alarm)"]:::aws
        SNS_Alerts["📣 SNS Topic: Alerts<br/>(fx-ingestion-alerts-topic-dev)"]:::aws
        SNS_Ready["📣 SNS Topic: Data Ready<br/>(fx-ingestion-data-ready-topic-dev)"]:::aws
    end

    %% Flows
    Cron -->|Daily Trigger 08:00 UTC| Lambda
    Lambda -->|1. Fetches Exchange Rates| API["🌐 Frankfurter API (External)"]:::external
    Lambda -->|2. Saves Partitioned JSON File| S3
    
    Lambda -.->|Emits Error Metrics >= 1| Alarm
    Alarm -->|Alarm Active| SNS_Alerts
    SNS_Alerts -->|Urgent Notification| Ops["👥 Operations/Data Team"]:::client

    S3 -->|3. Object Created Event (via S3 Notification)| S3_Event
    S3_Event -->|Publishes Ingestion Complete Event| SNS_Ready
    SNS_Ready -->|Data Ready Notification| Consumers["💻 Downstream Consumers (BI/Analytics)"]:::client

    S3 -.->|Partitions Referenced by Metadata| Glue
```

### Resource Catalog & Roles

1. **`aws_cloudwatch_event_rule.daily_trigger` (CRON)**:
   * **Role**: Orchestrates the timed execution.
   * **Behavior**: Fires daily to invoke the Lambda function, acting as the system's schedule coordinator.
2. **`aws_lambda_function.fx_ingestor`**:
   * **Role**: The core compute engine.
   * **Behavior**: Fetches exchange rates from the external API, parses the payload, validates business rules, and persists raw files to S3.
3. **`data.aws_s3_bucket.fx_raw_data`**:
   * **Role**: The centralized data lake storage.
   * **Behavior**: Stores exchange rates in partitioned folders (`raw/year=YYYY/month=MM/day=DD/`).
4. **`aws_cloudwatch_metric_alarm.lambda_error_alarm`**:
   * **Role**: Health monitoring sensor.
   * **Behavior**: Watches the error metric of the Lambda. If executions fail, it changes state to `ALARM` and triggers the operations SNS topic.
5. **`aws_sns_topic.data_team_alerts`**:
   * **Role**: Urgent alerting channel.
   * **Behavior**: Receives failures messages and dispatches alerts directly to the engineering team.
6. **`aws_s3_bucket_notification.bucket_notification`**:
   * **Role**: Storage event publisher.
   * **Behavior**: Intercepts files created in the S3 bucket and forwards them to AWS EventBridge default bus.
7. **`aws_cloudwatch_event_rule.s3_raw_upload_rule`**:
   * **Role**: Event router.
   * **Behavior**: Filters incoming S3 events to capture only successful file creations under the `raw/` partition and forwards them to the downstream SNS topic.
8. **`aws_sns_topic.data_ready_alerts`**:
   * **Role**: Success publication channel.
   * **Behavior**: Notifies downstream analytics and databases that the day's ingestion is finished and ready for consumption.
