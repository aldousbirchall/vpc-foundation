# REQ-009: S3 Bucket for Static Assets
# Validates S3 bucket creation using mock provider.
#
# AC-009-1: S3 bucket exists
# AC-009-4: Public access blocked

mock_provider "aws" {}

variables {
  region             = "eu-west-1"
  environment        = "test"
  project            = "vpc-test"
  owner              = "test-agent"
}

run "s3_bucket_created" {
  command = plan

  assert {
    condition     = length([for b in planned_values.root_module.resources : b if b.type == "aws_s3_bucket"]) >= 1
    error_message = "No S3 bucket found in plan"
  }
}

run "s3_public_access_block_created" {
  command = plan

  assert {
    condition     = length([for pab in planned_values.root_module.resources : pab if pab.type == "aws_s3_bucket_public_access_block"]) >= 1
    error_message = "No S3 public access block resource found"
  }
}

run "s3_versioning_configured" {
  command = plan

  assert {
    condition     = length([for v in planned_values.root_module.resources : v if v.type == "aws_s3_bucket_versioning"]) >= 1
    error_message = "No S3 bucket versioning resource found"
  }
}

run "s3_encryption_configured" {
  command = plan

  assert {
    condition     = length([for e in planned_values.root_module.resources : e if e.type == "aws_s3_bucket_server_side_encryption_configuration"]) >= 1
    error_message = "No S3 server-side encryption configuration found"
  }
}
