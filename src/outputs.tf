output "vpc_id" {
  value       = module.networking.vpc_id
  description = "ID of the VPC"
}

output "public_subnet_ids" {
  value       = module.networking.public_subnet_ids
  description = "IDs of the public subnets"
}

output "private_subnet_ids" {
  value       = module.networking.private_subnet_ids
  description = "IDs of the private subnets"
}

output "nat_gateway_id" {
  value       = module.networking.nat_gateway_id
  description = "ID of the NAT gateway"
}

output "internet_gateway_id" {
  value       = module.networking.internet_gateway_id
  description = "ID of the internet gateway"
}

output "web_security_group_id" {
  value       = module.security.web_security_group_id
  description = "ID of the web tier security group"
}

output "app_security_group_id" {
  value       = module.security.app_security_group_id
  description = "ID of the application tier security group"
}

output "bucket_id" {
  value       = module.storage.bucket_id
  description = "ID of the S3 bucket"
}

output "bucket_arn" {
  value       = module.storage.bucket_arn
  description = "ARN of the S3 bucket"
}
