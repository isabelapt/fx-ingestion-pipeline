# Declaração das entradas (parâmetros da linha de comando ou .tfvars)

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "Região AWS onde os recursos serão implantados"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Ambiente (dev, staging, prod)"
}

variable "bucket_prefix" {
  type        = string
  default     = "fx-ingestion-raw-data"
  description = "Prefixo do nome do Bucket S3"
}

variable "force_destroy" {
  type        = bool
  default     = false
  description = "Se verdadeiro, permite apagar o bucket S3 mesmo com objetos dentro ao rodar terraform destroy"
}

variable "lambda_timeout" {
  type        = number
  default     = 30
  description = "Timeout em segundos da execução da Lambda"
}

variable "cron_schedule" {
  type        = string
  default     = "cron(0 8 * * ? *)"
  description = "Expressão de agendamento do EventBridge"
}

variable "alert_email" {
  type        = string
  description = "E-mail de destino para alertas do pipeline (injetado em tempo de execução)"
  default     = ""
}

variable "aws_account_id" {
  type        = string
  description = "AWS Account ID used for importing resources and setting up ARNs"
  default     = ""
}