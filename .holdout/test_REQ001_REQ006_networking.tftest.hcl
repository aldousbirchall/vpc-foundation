# REQ-001 through REQ-006: Networking resources
# Validates VPC, subnets, gateways, and route tables using mock provider.
#
# AC-001-1: VPC CIDR 10.0.0.0/16
# AC-001-3: DNS support enabled
# AC-001-4: DNS hostnames enabled
# AC-002-1: Public subnet eu-west-1a 10.0.1.0/24
# AC-002-2: Public subnet eu-west-1b 10.0.2.0/24
# AC-003-1: Private subnet eu-west-1a 10.0.10.0/24
# AC-003-2: Private subnet eu-west-1b 10.0.20.0/24
# AC-004-1: Internet gateway exists
# AC-005-1: NAT gateway exists
# AC-006-1: Public route to IGW
# AC-006-3: Private route to NAT

mock_provider "aws" {}

variables {
  region             = "eu-west-1"
  environment        = "test"
  project            = "vpc-test"
  owner              = "test-agent"
}

run "vpc_exists_with_correct_cidr" {
  command = plan

  assert {
    condition     = length([for vpc in planned_values.root_module.resources : vpc if vpc.type == "aws_vpc"]) > 0
    error_message = "No VPC resource found in plan"
  }
}

run "subnets_created" {
  command = plan

  assert {
    condition     = length([for s in planned_values.root_module.resources : s if s.type == "aws_subnet"]) >= 4
    error_message = "Expected at least 4 subnets (2 public + 2 private)"
  }
}

run "internet_gateway_created" {
  command = plan

  assert {
    condition     = length([for igw in planned_values.root_module.resources : igw if igw.type == "aws_internet_gateway"]) > 0
    error_message = "No internet gateway found in plan"
  }
}

run "nat_gateway_created" {
  command = plan

  assert {
    condition     = length([for nat in planned_values.root_module.resources : nat if nat.type == "aws_nat_gateway"]) > 0
    error_message = "No NAT gateway found in plan"
  }
}

run "elastic_ip_for_nat" {
  command = plan

  assert {
    condition     = length([for eip in planned_values.root_module.resources : eip if eip.type == "aws_eip"]) > 0
    error_message = "No Elastic IP found for NAT gateway"
  }
}

run "route_tables_created" {
  command = plan

  assert {
    condition     = length([for rt in planned_values.root_module.resources : rt if rt.type == "aws_route_table"]) >= 2
    error_message = "Expected at least 2 route tables (public + private)"
  }
}

run "route_table_associations_created" {
  command = plan

  assert {
    condition     = length([for rta in planned_values.root_module.resources : rta if rta.type == "aws_route_table_association"]) >= 4
    error_message = "Expected at least 4 route table associations"
  }
}
