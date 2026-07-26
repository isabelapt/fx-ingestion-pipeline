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

# S3 Bucket para persistência dos dados raw
resource "aws_s3_bucket" "fx_raw_data" {
  bucket = "${var.bucket_prefix}-${var.environment}"

  force_destroy = var.environment == "dev" ? true : false
}

# Criptografia SSE-S3
resource "aws_s3_bucket_server_side_encryption_configuration" "fx_raw_data_crypto" {
  bucket = aws_s3_bucket.fx_raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bloqueio de Acesso Público
resource "aws_s3_bucket_public_access_block" "fx_raw_data_public_block" {
  bucket = aws_s3_bucket.fx_raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}