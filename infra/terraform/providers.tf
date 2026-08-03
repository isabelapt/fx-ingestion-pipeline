# Conexão e credenciais com provedores (AWS, GCP, etc.)

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