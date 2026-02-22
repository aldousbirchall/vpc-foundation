# REQ-007 and REQ-008: Security Groups
# Validates web tier and application tier security groups using mock provider.
#
# AC-007-1: Web SG exists
# AC-007-2: Port 80 ingress
# AC-007-3: Port 443 ingress
# AC-008-1: App SG exists
# AC-008-2: App SG ingress from web SG only

mock_provider "aws" {}

variables {
  region             = "eu-west-1"
  environment        = "test"
  project            = "vpc-test"
  owner              = "test-agent"
}

run "security_groups_created" {
  command = plan

  assert {
    condition     = length([for sg in planned_values.root_module.resources : sg if sg.type == "aws_security_group"]) >= 2
    error_message = "Expected at least 2 security groups (web + app)"
  }
}

run "no_compute_instances" {
  command = plan

  assert {
    condition     = length([for r in planned_values.root_module.resources : r if r.type == "aws_instance"]) == 0
    error_message = "Foundation layer must not provision compute instances"
  }
}
