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
			"Resource": "arn:aws:lambda:us-east-1:230850604130:function:fx-rate-ingestor-dev"
		},
		{
			"Sid": "CloudWatchAlarmsAccess",
			"Effect": "Allow",
			"Action": [
				"cloudwatch:PutMetricAlarm",
				"cloudwatch:DeleteAlarms"
			],
			"Resource": "arn:aws:cloudwatch:us-east-1:230850604130:alarm:fx-ingestor-error-alarm-dev"
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
				"arn:aws:events:us-east-1:230850604130:rule/fx-ingestion-daily-cron-dev",
				"arn:aws:events:us-east-1:230850604130:rule/fx-s3-raw-upload-rule-dev"
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
				"arn:aws:sns:us-east-1:230850604130:fx-ingestion-alerts-topic-dev",
				"arn:aws:sns:us-east-1:230850604130:fx-ingestion-data-ready-topic-dev"
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
				"arn:aws:glue:us-east-1:230850604130:catalog",
				"arn:aws:glue:us-east-1:230850604130:database/fx_rates_db_dev"
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
			"Resource": "arn:aws:iam::230850604130:role/fx-ingestion-lambda-role-dev"
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
			"Resource": "arn:aws:iam::230850604130:policy/fx-lambda-s3-write-dev"
		}
	]
}
```

### Explicação Detalhada de cada Ação por Serviço

#### 🪣 Serviço: S3 (Resource: `fx-ingestion-raw-data-dev`)
* `s3:CreateBucket` / `s3:DeleteBucket`: Permite ao Terraform provisionar e remover o bucket do Data Lake.
* `s3:ListBucket` / `s3:GetBucketLocation`: Permite ao Terraform verificar se o bucket existe e em qual região geográfica ele reside.
* `s3:PutEncryptionConfiguration` / `s3:GetEncryptionConfiguration`: Garante a criptografia em repouso dos dados no bucket.
* `s3:PutBucketPublicAccessBlock` / `s3:GetBucketPublicAccessBlock`: Habilita o bloqueio total contra acesso público não autorizado.
* `s3:PutBucketNotification` / `s3:GetBucketNotification`: Configura as notificações nativas no bucket para acionar o fluxo de mensagens.

#### ⚡ Serviço: Lambda (Resource: `fx-rate-ingestor-dev`)
* `lambda:CreateFunction` / `lambda:DeleteFunction`: Cria e deleta o código/ambiente da Lambda de ingestão.
* `lambda:UpdateFunctionCode` / `lambda:UpdateFunctionConfiguration`: Faz upload do novo pacote ZIP e atualiza variáveis de ambiente.
* `lambda:AddPermission` / `lambda:RemovePermission`: Permite associar gatilhos externos à Lambda (como regras cron do EventBridge).
* `lambda:GetFunctionCodeSigningConfig` / `lambda:ListVersionsByFunction`: Utilizados pelo provider Terraform para controle de versões e integridade.
* `lambda:PutFunctionEventInvokeConfig` / `lambda:GetFunctionEventInvokeConfig`: Configura a política de retry assíncrono (quantas tentativas fazer antes de desistir).

#### 🚨 Serviço: CloudWatch Alarms (Resource: `fx-ingestor-error-alarm-dev`)
* `cloudwatch:PutMetricAlarm` / `cloudwatch:DeleteAlarms`: Cria e destrói o alarme de erros da Lambda.
* `cloudwatch:DescribeAlarms` (Resource: `*`): Lista os alarmes existentes na conta durante a execução do `terraform plan` (a AWS exige escopo global para essa leitura).

#### 📨 Serviço: EventBridge Rules (Resource: `fx-ingestion-daily-cron-dev` e `fx-s3-raw-upload-rule-dev`)
* `events:PutRule` / `events:DeleteRule` / `events:DescribeRule`: Cria, atualiza e deleta as regras de gatilho (cron e escuta do S3).
* `events:PutTargets` / `events:RemoveTargets` / `events:ListTargetsByRule`: Mapeia quais recursos (Lambda, SNS) serão chamados quando as regras forem ativadas.

#### 📣 Serviço: SNS (Resource: tópicos `fx-ingestion-alerts-topic-dev` e `fx-ingestion-data-ready-topic-dev`)
* `sns:CreateTopic` / `sns:DeleteTopic`: Cria e deleta os canais de mensagens SNS.
* `sns:SetTopicAttributes` / `sns:GetTopicAttributes`: Permite alterar configurações e políticas do tópico (como dar permissão para o CloudWatch/EventBridge publicarem dados nele).

#### 🗄️ Serviço: Glue Catalog (Resource: `catalog` e `fx_rates_db_dev`)
* `glue:CreateDatabase` / `glue:GetDatabase` / `glue:UpdateDatabase` / `glue:DeleteDatabase`: Registra e mantém o banco de dados de metadados no Glue, permitindo consultas Athena sobre o bucket raw.

#### 🔑 Serviço: IAM (Resource: role `fx-ingestion-lambda-role-dev` e policy `fx-lambda-s3-write-dev`)
* `iam:CreateRole` / `iam:GetRole` / `iam:DeleteRole` / `iam:PassRole`: Gerencia o ciclo de vida da role de execução da Lambda e a repassa para que o serviço da Lambda a utilize.
* `iam:AttachRolePolicy` / `iam:DetachRolePolicy`: Associa políticas de permissão (como permissão de escrita em S3) à role da Lambda.
* `iam:CreatePolicy` / `iam:GetPolicy` / `iam:DeletePolicy` / `iam:CreatePolicyVersion`: Gerencia a política customizada específica que concede privilégios de S3 à Lambda.

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

The following diagram illustrates how the AWS resources deployed by Terraform connect with each other, defining both the **Scheduled Ingestion Flow**, the **Error Handling Flow**, and the **Downstream Event Integration Flow**:

```mermaid
flowchart TB
    %% Nodes styling
    classDef aws fill:#232F3E,stroke:#FF9900,stroke-width:2px,color:white;
    classDef client fill:#1A73E8,stroke:#0F9D58,stroke-width:2px,color:white;
    classDef external fill:#7A7A7A,stroke:#333333,stroke-width:2px,color:white;
    
    subgraph Triggers ["Gatilhos & Eventos"]
        Cron["⏰ EventBridge Cron<br/>(daily_trigger)"]:::aws
        S3_Event["📨 EventBridge Rule<br/>(s3_raw_upload_rule)"]:::aws
    end

    subgraph Computing ["Computação & Lógica"]
        Lambda["⚡ AWS Lambda<br/>(fx-rate-ingestor-dev)"]:::aws
    end

    subgraph StorageCatalog ["Armazenamento & Metadados"]
        S3["🪣 S3 Raw Bucket<br/>(fx-ingestion-raw-data-dev)"]:::aws
        Glue["🗄️ Glue Catalog Database<br/>(fx_rates_db_dev)"]:::aws
    end

    subgraph Observers ["Monitoramento & Alertas"]
        Alarm["🚨 CloudWatch Metric Alarm<br/>(lambda_error_alarm)"]:::aws
        SNS_Alerts["📣 SNS Topic: Alerts<br/>(fx-ingestion-alerts-topic-dev)"]:::aws
        SNS_Ready["📣 SNS Topic: Data Ready<br/>(fx-ingestion-data-ready-topic-dev)"]:::aws
    end

    %% Flows
    Cron -->|Gatilho Diário 08:00 UTC| Lambda
    Lambda -->|1. Consome Taxas de Câmbio| API["🌐 Frankfurter API (External)"]:::external
    Lambda -->|2. Salva Arquivo JSON Particionado| S3
    
    Lambda -.->|Gera Métricas de Errors >= 1| Alarm
    Alarm -->|Alarme Ativo| SNS_Alerts
    SNS_Alerts -->|Notificação Urgente| Ops["👥 Equipe de Operações (Data Team)"]:::client

    S3 -->|3. Evento Object Created (via S3 Notification)| S3_Event
    S3_Event -->|Publica Confirmação de Ingestão Concluída| SNS_Ready
    SNS_Ready -->|Notificação de Dados Prontos| Consumers["💻 Consumidores Downstream (BI/Analytics)"]:::client

    S3 -.->|Partições Referenciadas por Metadados| Glue
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

