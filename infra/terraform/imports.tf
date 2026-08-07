import {
  to = aws_iam_role.lambda_exec_role
  id = "fx-ingestion-lambda-role-dev"
}

import {
  to = aws_iam_policy.lambda_s3_policy
  id = "arn:aws:iam::${var.aws_account_id}:policy/fx-lambda-s3-write-dev"
}

import {
  to = aws_glue_catalog_database.fx_database
  id = "${var.aws_account_id}:fx_rates_db_dev"
}

import {
  to = aws_cloudwatch_event_rule.daily_trigger
  id = "fx-ingestion-daily-cron-dev"
}

import {
  to = aws_sns_topic.data_team_alerts
  id = "arn:aws:sns:us-east-1:${var.aws_account_id}:fx-ingestion-alerts-topic-dev"
}

import {
  to = aws_s3_bucket_notification.bucket_notification
  id = "fx-ingestion-raw-data-dev"
}

import {
  to = aws_sns_topic.data_ready_alerts
  id = "arn:aws:sns:us-east-1:${var.aws_account_id}:fx-ingestion-data-ready-topic-dev"
}

import {
  to = aws_cloudwatch_event_rule.s3_raw_upload_rule
  id = "fx-s3-raw-upload-rule-dev"
}

import {
  to = aws_lambda_function.fx_ingestor
  id = "fx-rate-ingestor-dev"
}
