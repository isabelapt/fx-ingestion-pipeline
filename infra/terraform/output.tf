output "s3_bucket_name" {
  value       = data.aws_s3_bucket.fx_raw_data.id
  description = "Name of the existing S3 bucket for raw FX data"
}

output "s3_bucket_arn" {
  value       = data.aws_s3_bucket.fx_raw_data.arn
  description = "ARN of the S3 bucket"
}