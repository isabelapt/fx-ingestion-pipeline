# S3 Bucket for raw data persistence
data "aws_s3_bucket" "fx_raw_data" {
  bucket = local.bucket_name
}

# # SSE-S3 Encryption Configuration
# resource "aws_s3_bucket_server_side_encryption_configuration" "fx_raw_data_crypto" {
#   bucket = data.aws_s3_bucket.fx_raw_data.id
# 
#   rule {
#     apply_server_side_encryption_by_default {
#       sse_algorithm = "AES256"
#     }
#   }
# }
# 
# # Public Access Block Configuration
# resource "aws_s3_bucket_public_access_block" "fx_raw_data_public_block" {
#   bucket = data.aws_s3_bucket.fx_raw_data.id
# 
#   block_public_acls       = true
#   block_public_policy     = true
#   ignore_public_acls      = true
#   restrict_public_buckets = true
# }
# 
# # S3 Lifecycle Configuration for Data Retention and Cost Optimization
# resource "aws_s3_bucket_lifecycle_configuration" "fx_raw_data_lifecycle" {
#   bucket = data.aws_s3_bucket.fx_raw_data.id
# 
#   rule {
#     id     = "archive-and-cleanup"
#     status = "Enabled"
# 
#     filter {}
# 
#     transition {
#       days          = 90
#       storage_class = "GLACIER"
#     }
# 
#     expiration {
#       days = 365
#     }
#   }
# }

# Enable S3 Event notification flow to default EventBridge bus
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket      = data.aws_s3_bucket.fx_raw_data.id
  eventbridge = true
}