output "web_security_group_id" {
  value       = aws_security_group.web.id
  description = "ID of the web tier security group"
}

output "app_security_group_id" {
  value       = aws_security_group.app.id
  description = "ID of the application tier security group"
}
