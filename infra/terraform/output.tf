output "s3_bucket_name" {
  value       = aws_s3_bucket.fx_raw_data.id
  description = "Name of the created S3 bucket for raw FX data"
}

output "s3_bucket_arn" {
  value       = aws_s3_bucket.fx_raw_data.arn
  description = "ARN of the S3 bucket"
}