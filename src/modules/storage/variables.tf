variable "bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment name for resource naming"
}

variable "project" {
  type        = string
  default     = "vpc-foundation"
  description = "Project name for resource naming"
}
