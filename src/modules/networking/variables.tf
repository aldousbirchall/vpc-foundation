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
