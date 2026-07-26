variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for provisioning resources"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Deployment environment (dev, staging, prod)"
}

variable "bucket_prefix" {
  type        = string
  default     = "fx-ingestion-raw-data"
  description = "Prefix for the S3 bucket name"
}