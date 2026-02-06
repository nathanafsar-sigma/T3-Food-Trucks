variable "aws_region" {
  description = "AWS region for the S3 bucket"
  type        = string
}

variable "AWS_ACCESS_KEY" {
  description = "AWS access key ID"
  type        = string
  sensitive   = true
}

variable "AWS_SECRET_KEY" {
  description = "AWS secret access key"
  type        = string
  sensitive   = true
}

variable "bucket_name" {
  description = "Name of the S3 bucket for the data lake (must be globally unique)"
  type        = string
}

variable "ecr_repository_url" {
  description = "URL of the ECR repository containing the pipeline image"
  type        = string
}

variable "ses_sender_email" {
  description = "Email address to send reports from (must be verified in SES)"
  type        = string
}

variable "ses_recipient_email" {
  description = "Email address to send reports to"
  type        = string
}

variable "db_host" {
  description = "RDS database host"
  type        = string
  sensitive   = true
}

variable "db_port" {
  description = "RDS database port"
  type        = string
}

variable "db_user" {
  description = "RDS database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "RDS database password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "RDS database name"
  type        = string
  sensitive   = true
}

variable "schedule_expression" {
  description = "Schedule expression for running the ETL pipeline (e.g., 'cron(0 12,15,18,21 * * ? *)' for multiple times)"
  type        = string
}