output "vpc_id" {
  value       = aws_vpc.main.id
  description = "ID of the VPC"
}

output "public_subnet_ids" {
  value       = aws_subnet.public[*].id
  description = "IDs of the public subnets"
}

output "private_subnet_ids" {
  value       = aws_subnet.private[*].id
  description = "IDs of the private subnets"
}

output "nat_gateway_id" {
  value       = aws_nat_gateway.main.id
  description = "ID of the NAT gateway"
}

output "internet_gateway_id" {
  value       = aws_internet_gateway.main.id
  description = "ID of the internet gateway"
}
