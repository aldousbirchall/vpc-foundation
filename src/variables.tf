variable "region" {
  type        = string
  default     = "eu-west-1"
  description = "AWS region for all resources"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment name (e.g. dev, staging, prod)"
}

variable "project" {
  type        = string
  default     = "vpc-foundation"
  description = "Project name used in resource naming and tags"
}

variable "owner" {
  type        = string
  description = "Owner tag value for cost attribution"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR block for the VPC"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
  description = "CIDR blocks for public subnets"
}

variable "private_subnet_cidrs" {
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
  description = "CIDR blocks for private subnets"
}

variable "availability_zones" {
  type        = list(string)
  default     = ["eu-west-1a", "eu-west-1b"]
  description = "Availability zones for subnet placement"
}

variable "bucket_name" {
  type        = string
  description = "Globally unique name for the static assets S3 bucket"
}

variable "max_instance_size" {
  type        = string
  default     = "t3.large"
  description = "Maximum allowed instance size (advisory, for future compute)"
}
