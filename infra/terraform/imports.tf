import {
  to = aws_iam_role.lambda_exec_role
  id = "fx-ingestion-lambda-role-${var.environment}"
}

import {
  to = aws_iam_policy.lambda_s3_policy
  id = "arn:aws:iam::230850604130:policy/fx-lambda-s3-write-${var.environment}"
}

import {
  to = aws_glue_catalog_database.fx_database
  id = "230850604130:fx_rates_db_${var.environment}"
}

import {
  to = aws_cloudwatch_event_rule.daily_trigger
  id = "fx-ingestion-daily-cron-${var.environment}"
}

import {
  to = aws_sns_topic.data_team_alerts
  id = "arn:aws:sns:us-east-1:230850604130:fx-ingestion-alerts-topic-${var.environment}"
}

import {
  to = aws_s3_bucket_notification.bucket_notification
  id = "fx-ingestion-raw-data-${var.environment}"
}

import {
  to = aws_sns_topic.data_ready_alerts
  id = "arn:aws:sns:us-east-1:230850604130:fx-ingestion-data-ready-topic-${var.environment}"
}

import {
  to = aws_cloudwatch_event_rule.s3_raw_upload_rule
  id = "fx-s3-raw-upload-rule-${var.environment}"
}
