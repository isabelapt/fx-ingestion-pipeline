terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "fx-ingestion-pipeline"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# S3 Bucket for raw data persistence
resource "aws_s3_bucket" "fx_raw_data" {
  bucket = "${var.bucket_prefix}-${var.environment}"

  force_destroy = var.environment == "dev" || var.environment == "staging" ? true : var.force_destroy
}

# SSE-S3 Encryption Configuration
resource "aws_s3_bucket_server_side_encryption_configuration" "fx_raw_data_crypto" {
  bucket = aws_s3_bucket.fx_raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Public Access Block Configuration
resource "aws_s3_bucket_public_access_block" "fx_raw_data_public_block" {
  bucket = aws_s3_bucket.fx_raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


# -----------------------------------------------------------------------------
# IAM ROLE & POLICIES FOR AWS LAMBDA
# -----------------------------------------------------------------------------
resource "aws_iam_role" "lambda_exec_role" {
  name = "fx-ingestion-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Basic execution policy for generating CloudWatch logs
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Least-privilege policy allowing Lambda to write only to our S3 Bucket
resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "fx-lambda-s3-write-${var.environment}"
  description = "Allows Lambda to write raw FX rate payloads into S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:PutObject", "s3:GetObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.fx_raw_data.arn,
        "${aws_s3_bucket.fx_raw_data.arn}/*"
      ]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}

# -----------------------------------------------------------------------------
# PYTHON APPLICATION ZIP PACKAGING
# -----------------------------------------------------------------------------

# Install dependencies and prepare Lambda package
resource "null_resource" "lambda_dependencies" {
  triggers = {
    pyproject = filemd5("${path.module}/../../pyproject.toml")
    src_hash  = sha1(join("", [for f in fileset("${path.module}/../../src", "**") : filemd5("${path.module}/../../src/${f}")]))
  }

  provisioner "local-exec" {
    command = <<-EOT
      rm -rf ${path.module}/lambda_staging
      mkdir -p ${path.module}/lambda_staging
      pip install --target ${path.module}/lambda_staging httpx pydantic
      cp -r ${path.module}/../../src/* ${path.module}/lambda_staging/
    EOT
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_staging"
  output_path = "${path.module}/lambda_payload.zip"

  depends_on = [null_resource.lambda_dependencies]
}

# -----------------------------------------------------------------------------
# AWS LAMBDA FUNCTION RESOURCE
# -----------------------------------------------------------------------------
resource "aws_lambda_function" "fx_ingestor" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "fx-rate-ingestor-${var.environment}"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "adapters.lambda_handler.lambda_handler"
  runtime          = "python3.12"
  timeout          = var.lambda_timeout
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  environment {
    variables = {
      ENVIRONMENT    = var.environment
      S3_BUCKET_NAME = aws_s3_bucket.fx_raw_data.id
    }
  }
}

# -----------------------------------------------------------------------------
# AWS EVENTBRIDGE (DAILY CRON TRIGGER)
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "fx-ingestion-daily-cron-${var.environment}"
  description         = "Triggers daily FX rate ingestion at 08:00 AM UTC"
  schedule_expression = var.cron_schedule
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "TriggerFXLambda"
  arn       = aws_lambda_function.fx_ingestor.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fx_ingestor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}

# -----------------------------------------------------------------------------
# AWS LAMBDA ASYNCHRONOUS RETRIES CONFIGURATION
# -----------------------------------------------------------------------------
resource "aws_lambda_function_event_invoke_config" "fx_ingestor_async_config" {
  function_name          = aws_lambda_function.fx_ingestor.function_name
  maximum_retry_attempts = 2 # 1 initial execution + 2 retries = 3 total attempts
}

# -----------------------------------------------------------------------------
# NOTIFICATIONS & FAILURE ALARMS (SNS & CLOUDWATCH)
# -----------------------------------------------------------------------------
resource "aws_sns_topic" "data_team_alerts" {
  name = "fx-ingestion-alerts-topic-${var.environment}"
}

resource "aws_cloudwatch_metric_alarm" "lambda_error_alarm" {
  alarm_name          = "fx-ingestor-error-alarm-${var.environment}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300 # 5-minute evaluation window
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Triggered when the FX Rates Ingestor Lambda function fails (Errors >= 1) after retries."
  alarm_actions       = [aws_sns_topic.data_team_alerts.arn]

  dimensions = {
    FunctionName = aws_lambda_function.fx_ingestor.function_name
  }
}

# -----------------------------------------------------------------------------
# AWS GLUE DATABASE (DATA CATALOG FOR AMAZON ATHENA)
# -----------------------------------------------------------------------------
resource "aws_glue_catalog_database" "fx_database" {
  name = "fx_rates_db_${var.environment}"
}

# -----------------------------------------------------------------------------
# INGESTION COMPLETE NOTIFICATION (EVENT-DRIVEN PATTERN)
# -----------------------------------------------------------------------------

# Enable S3 Event notification flow to default EventBridge bus
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket      = aws_s3_bucket.fx_raw_data.id
  eventbridge = true
}

# SNS Topic to alert downstream analytics consumers that ingestion is finished
resource "aws_sns_topic" "data_ready_alerts" {
  name = "fx-ingestion-data-ready-topic-${var.environment}"
}

# EventBridge rule to intercept Object Created (PutObject) events under raw/ prefix
resource "aws_cloudwatch_event_rule" "s3_raw_upload_rule" {
  name        = "fx-s3-raw-upload-rule-${var.environment}"
  description = "Triggered when a new FX rate raw file is uploaded under raw/ partition in S3."

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["Object Created"]
    detail = {
      bucket = {
        name = [aws_s3_bucket.fx_raw_data.id]
      }
      object = {
        key = [{
          prefix = "raw/"
        }]
      }
    }
  })
}

# Route the success event captured by EventBridge to the SNS Topic
resource "aws_cloudwatch_event_target" "sns_data_ready_target" {
  rule      = aws_cloudwatch_event_rule.s3_raw_upload_rule.name
  target_id = "SendIngestionCompleteAlert"
  arn       = aws_sns_topic.data_ready_alerts.arn
}

# Allow EventBridge to publish messages into the data_ready SNS topic
resource "aws_sns_topic_policy" "data_ready_sns_policy" {
  arn = aws_sns_topic.data_ready_alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sns:Publish"
      Resource  = aws_sns_topic.data_ready_alerts.arn
      Condition = {
        ArnEquals = {
          "aws:SourceArn" = aws_cloudwatch_event_rule.s3_raw_upload_rule.arn
        }
      }
    }]
  })
}

# -----------------------------------------------------------------------------
# AWS GLUE CRAWLER REMOVED
# -----------------------------------------------------------------------------
# The Glue Crawler has been removed to avoid conflicts with the manual DDL
# table definition in queries/athena_queries.sql. The raw_fx_rates table
# is now managed exclusively through manual DDL and MSCK REPAIR TABLE commands.