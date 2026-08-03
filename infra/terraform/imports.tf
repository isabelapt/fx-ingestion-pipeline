import {
  to = aws_iam_role.lambda_exec_role
  id = local.import_lambda_role_id
}

import {
  to = aws_iam_policy.lambda_s3_policy
  id = local.import_lambda_s3_policy_id
}

import {
  to = aws_glue_catalog_database.fx_database
  id = local.import_glue_database_id
}

import {
  to = aws_cloudwatch_event_rule.daily_trigger
  id = local.import_daily_trigger_id
}

import {
  to = aws_sns_topic.data_team_alerts
  id = local.import_data_team_alerts_id
}

import {
  to = aws_s3_bucket_notification.bucket_notification
  id = local.import_bucket_notification_id
}

import {
  to = aws_sns_topic.data_ready_alerts
  id = local.import_data_ready_alerts_id
}

import {
  to = aws_cloudwatch_event_rule.s3_raw_upload_rule
  id = local.import_s3_raw_upload_rule_id
}
