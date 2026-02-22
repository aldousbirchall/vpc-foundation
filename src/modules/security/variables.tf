variable "vpc_id" {
  type        = string
  description = "VPC ID for security group placement"
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
