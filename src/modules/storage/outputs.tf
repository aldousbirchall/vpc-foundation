output "bucket_id" {
  value       = aws_s3_bucket.static_assets.id
  description = "ID of the S3 bucket"
}

output "bucket_arn" {
  value       = aws_s3_bucket.static_assets.arn
  description = "ARN of the S3 bucket"
}
