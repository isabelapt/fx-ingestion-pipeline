locals {
  bucket_name           = "${var.bucket_prefix}-${var.environment}"
  lambda_role_name      = "fx-ingestion-lambda-role-${var.environment}"
  lambda_s3_policy_name = "fx-lambda-s3-write-${var.environment}"
  glue_database_name    = "fx_rates_db_${var.environment}"
  sns_alerts_topic_name = "fx-ingestion-data-ready-topic-${var.environment}"
  event_rule_name       = "fx-s3-raw-upload-rule-${var.environment}"

  # Additional main resources
  lambda_function_name    = "fx-rate-ingestor-${var.environment}"
  daily_trigger_rule_name = "fx-ingestion-daily-cron-${var.environment}"

  # Notifications & failure alarms
  sns_data_team_alerts_topic_name = "fx-ingestion-alerts-topic-${var.environment}"
  lambda_error_alarm_name         = "fx-ingestor-error-alarm-${var.environment}"

  # Import block static ID values
  import_lambda_role_id         = "fx-ingestion-lambda-role-${var.environment}"
  import_lambda_s3_policy_id    = "arn:aws:iam::AWS_ACCOUNT_ID_PLACEHOLDER:policy/fx-lambda-s3-write-${var.environment}"
  import_glue_database_id       = "AWS_ACCOUNT_ID_PLACEHOLDER:fx_rates_db_${var.environment}"
  import_daily_trigger_id       = "fx-ingestion-daily-cron-${var.environment}"
  import_data_team_alerts_id    = "arn:aws:sns:us-east-1:AWS_ACCOUNT_ID_PLACEHOLDER:fx-ingestion-alerts-topic-${var.environment}"
  import_bucket_notification_id = "fx-ingestion-raw-data-${var.environment}"
  import_data_ready_alerts_id   = "arn:aws:sns:us-east-1:AWS_ACCOUNT_ID_PLACEHOLDER:fx-ingestion-data-ready-topic-${var.environment}"
  import_s3_raw_upload_rule_id  = "fx-s3-raw-upload-rule-${var.environment}"
}
