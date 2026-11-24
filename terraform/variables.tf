variable "aws_region" {
  description = "AWS Deployment Region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment Environment (staging / production)"
  type        = string
  default     = "production"
}

variable "app_name" {
  description = "Application Name identifier"
  type        = string
  default     = "enterprise-docintel"
}

variable "db_username" {
  description = "PostgreSQL Master Username"
  type        = string
  default     = "docintel_admin"
}

variable "db_password" {
  description = "PostgreSQL Master Password"
  type        = string
  sensitive   = true
  default     = "P@ssw0rdSecurePgVector2026!"
}

variable "ecs_cpu" {
  description = "Fargate Task CPU units (1024 = 1 vCPU)"
  type        = number
  default     = 1024
}

variable "ecs_memory" {
  description = "Fargate Task Memory in MiB (2048 = 2 GB)"
  type        = number
  default     = 2048
}
