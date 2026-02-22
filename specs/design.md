# Design Specification: vpc-foundation

## Architecture Overview

A two-tier VPC foundation in eu-west-1 providing the networking, security, and storage substrate for a web application. The VPC uses a /16 CIDR block split into public subnets (internet-facing, for future load balancers) and private subnets (for future application instances) across two availability zones. A single NAT gateway in a public subnet provides outbound internet access for private subnets. An S3 bucket provides versioned storage for static assets.

No compute resources are provisioned. This is a foundation-only build.

```
                    Internet
                       |
                 [Internet Gateway]
                       |
          +------------+------------+
          |                         |
  [Public Subnet 1]        [Public Subnet 2]
   10.0.1.0/24              10.0.2.0/24
   eu-west-1a               eu-west-1b
          |
     [NAT Gateway]
     (Elastic IP)
          |
          +------------+------------+
          |                         |
  [Private Subnet 1]       [Private Subnet 2]
   10.0.10.0/24             10.0.20.0/24
   eu-west-1a               eu-west-1b

  Security Groups:
    - web-sg:  ingress 80/443 from 0.0.0.0/0
    - app-sg:  ingress from web-sg only

  Storage:
    - S3 bucket (static assets, versioned, encrypted, private)
```

---

## Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| IaC tool | Terraform (HCL) | Industry standard for AWS infrastructure. Declarative, plannable, modular. |
| Terraform version | >= 1.5.0 | Stable feature set including import blocks and check blocks. |
| AWS provider | hashicorp/aws ~> 5.0 | Current major version with full eu-west-1 support. |
| Module structure | Separate modules per concern | Avoids monolithic configuration. Each module is independently testable. |
| Testing | terraform validate + terraform plan | Plan-only pipeline. No apply. Structural validation via HCL parsing. |
| Build tool | Make | Simple, universal, no additional dependencies. |
| State backend | S3 + DynamoDB | Standard Terraform remote state with locking and encryption. |
| Cost control | Single NAT gateway, no compute | Keeps baseline under $40/month against $150/month budget. |

---

## Components

### Module: networking

**Purpose**: VPC, subnets, internet gateway, NAT gateway, route tables, Elastic IP.

**Files**: `modules/networking/main.tf`, `modules/networking/variables.tf`, `modules/networking/outputs.tf`

**Resources**:

| Resource | Type | Notes |
|---|---|---|
| VPC | `aws_vpc` | CIDR 10.0.0.0/16, DNS support + hostnames enabled |
| Public Subnet 1 | `aws_subnet` | 10.0.1.0/24, eu-west-1a, map_public_ip_on_launch = true |
| Public Subnet 2 | `aws_subnet` | 10.0.2.0/24, eu-west-1b, map_public_ip_on_launch = true |
| Private Subnet 1 | `aws_subnet` | 10.0.10.0/24, eu-west-1a |
| Private Subnet 2 | `aws_subnet` | 10.0.20.0/24, eu-west-1b |
| Internet Gateway | `aws_internet_gateway` | Attached to VPC |
| Elastic IP | `aws_eip` | For NAT gateway |
| NAT Gateway | `aws_nat_gateway` | In public subnet 1, single-AZ for cost |
| Public Route Table | `aws_route_table` | 0.0.0.0/0 -> IGW |
| Private Route Table | `aws_route_table` | 0.0.0.0/0 -> NAT GW |
| Public RT Associations (x2) | `aws_route_table_association` | Public subnets -> public RT |
| Private RT Associations (x2) | `aws_route_table_association` | Private subnets -> private RT |

**Variables**:

| Variable | Type | Default | Description |
|---|---|---|---|
| `vpc_cidr` | string | `"10.0.0.0/16"` | CIDR block for the VPC |
| `public_subnet_cidrs` | list(string) | `["10.0.1.0/24", "10.0.2.0/24"]` | CIDR blocks for public subnets |
| `private_subnet_cidrs` | list(string) | `["10.0.10.0/24", "10.0.20.0/24"]` | CIDR blocks for private subnets |
| `availability_zones` | list(string) | `["eu-west-1a", "eu-west-1b"]` | Availability zones for subnet placement |
| `environment` | string | `"dev"` | Environment name for resource naming |
| `project` | string | `"vpc-foundation"` | Project name for resource naming |

**Outputs**: `vpc_id`, `public_subnet_ids`, `private_subnet_ids`, `nat_gateway_id`, `internet_gateway_id`

---

### Module: security

**Purpose**: Security groups for web and application tiers.

**Files**: `modules/security/main.tf`, `modules/security/variables.tf`, `modules/security/outputs.tf`

**Resources**:

| Resource | Type | Notes |
|---|---|---|
| Web Security Group | `aws_security_group` | Ingress: TCP 80 and 443 from 0.0.0.0/0. Egress: all. |
| Web SG Ingress HTTP | `aws_vpc_security_group_ingress_rule` | Port 80, 0.0.0.0/0 |
| Web SG Ingress HTTPS | `aws_vpc_security_group_ingress_rule` | Port 443, 0.0.0.0/0 |
| Web SG Egress | `aws_vpc_security_group_egress_rule` | All traffic |
| App Security Group | `aws_security_group` | Ingress: from web SG only. Egress: all. |
| App SG Ingress | `aws_vpc_security_group_ingress_rule` | All ports, source = web SG |
| App SG Egress | `aws_vpc_security_group_egress_rule` | All traffic |

**Variables**:

| Variable | Type | Default | Description |
|---|---|---|---|
| `vpc_id` | string | (required) | VPC ID for security group placement |
| `environment` | string | `"dev"` | Environment name for resource naming |
| `project` | string | `"vpc-foundation"` | Project name for resource naming |

**Outputs**: `web_security_group_id`, `app_security_group_id`

**Design Note**: Security group rules use the standalone `aws_vpc_security_group_ingress_rule` and `aws_vpc_security_group_egress_rule` resources rather than inline rules. This avoids the well-known Terraform issue where inline and standalone rules conflict and cause perpetual diffs.

---

### Module: storage

**Purpose**: S3 bucket for static assets.

**Files**: `modules/storage/main.tf`, `modules/storage/variables.tf`, `modules/storage/outputs.tf`

**Resources**:

| Resource | Type | Notes |
|---|---|---|
| S3 Bucket | `aws_s3_bucket` | Name from variable |
| Bucket Versioning | `aws_s3_bucket_versioning` | Enabled |
| Server-Side Encryption | `aws_s3_bucket_server_side_encryption_configuration` | AES256 |
| Public Access Block | `aws_s3_bucket_public_access_block` | All four settings true |

**Variables**:

| Variable | Type | Default | Description |
|---|---|---|---|
| `bucket_name` | string | (required) | Globally unique S3 bucket name |
| `environment` | string | `"dev"` | Environment name for resource naming |
| `project` | string | `"vpc-foundation"` | Project name for resource naming |

**Outputs**: `bucket_id`, `bucket_arn`

---

### Root Module

**Purpose**: Wire modules together, define provider configuration, set default tags.

**Files**: `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`, `backend.tf`

**providers.tf**:
```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project
      Owner       = var.owner
      ManagedBy   = "terraform"
    }
  }
}
```

**backend.tf**:
```hcl
terraform {
  backend "s3" {
    bucket         = "vpc-foundation-tfstate"
    key            = "vpc-foundation/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "vpc-foundation-tflock"
  }
}
```

**Root Variables**:

| Variable | Type | Default | Description |
|---|---|---|---|
| `region` | string | `"eu-west-1"` | AWS region for all resources |
| `environment` | string | `"dev"` | Environment name (e.g. dev, staging, prod) |
| `project` | string | `"vpc-foundation"` | Project name used in resource naming and tags |
| `owner` | string | (required) | Owner tag value for cost attribution |
| `vpc_cidr` | string | `"10.0.0.0/16"` | CIDR block for the VPC |
| `public_subnet_cidrs` | list(string) | `["10.0.1.0/24", "10.0.2.0/24"]` | CIDR blocks for public subnets |
| `private_subnet_cidrs` | list(string) | `["10.0.10.0/24", "10.0.20.0/24"]` | CIDR blocks for private subnets |
| `availability_zones` | list(string) | `["eu-west-1a", "eu-west-1b"]` | Availability zones |
| `bucket_name` | string | (required) | Globally unique name for the static assets S3 bucket |
| `max_instance_size` | string | `"t3.large"` | Maximum allowed instance size (advisory, for future compute) |

---

## Network Topology

```
VPC: 10.0.0.0/16 (65,536 addresses)
|
+-- Public Subnets (internet-routable via IGW)
|   +-- 10.0.1.0/24  (256 addresses, eu-west-1a)
|   +-- 10.0.2.0/24  (256 addresses, eu-west-1b)
|
+-- Private Subnets (outbound-only via NAT GW)
    +-- 10.0.10.0/24 (256 addresses, eu-west-1a)
    +-- 10.0.20.0/24 (256 addresses, eu-west-1b)

Route Tables:
  public-rt:  local + 0.0.0.0/0 -> IGW
  private-rt: local + 0.0.0.0/0 -> NAT GW
```

---

## IAM Strategy

No IAM roles or policies are created in this build. There are no compute resources to assume roles. The S3 bucket relies on the public access block and default encryption configuration rather than a bucket policy. IAM will be added when compute resources are introduced in a subsequent build.

---

## Encryption

| Resource | Encryption | Mechanism |
|---|---|---|
| Static assets S3 bucket | At rest | SSE-S3 (AES256) default encryption |
| Terraform state S3 bucket | At rest | Backend `encrypt = true` (SSE-S3) |
| Data in transit | N/A | No compute; HTTPS enforced by AWS APIs |

---

## State Management

Terraform state is stored in an S3 bucket with DynamoDB-based locking. The state backend bucket and DynamoDB table are assumed to exist prior to `terraform init` (they are not managed by this configuration).

| Component | Resource | Notes |
|---|---|---|
| State storage | S3 bucket `vpc-foundation-tfstate` | Versioned, encrypted |
| State locking | DynamoDB table `vpc-foundation-tflock` | Prevents concurrent modifications |
| State path | `vpc-foundation/terraform.tfstate` | Single workspace |

---

## Resource Naming Convention

Pattern: `{project}-{environment}-{resource}`

Examples:
- VPC: `vpc-foundation-dev-vpc`
- Public Subnet 1: `vpc-foundation-dev-public-1`
- Private Subnet 1: `vpc-foundation-dev-private-1`
- Internet Gateway: `vpc-foundation-dev-igw`
- NAT Gateway: `vpc-foundation-dev-nat`
- Web Security Group: `vpc-foundation-dev-web-sg`
- App Security Group: `vpc-foundation-dev-app-sg`

The `Name` tag follows this convention. Default tags (Environment, Project, Owner, ManagedBy) are applied via the provider block.

---

## Cost Estimate

| Resource | Monthly Cost (USD) | Notes |
|---|---|---|
| NAT Gateway | ~$32.40 | $0.045/hr fixed |
| Elastic IP (attached) | $0.00 | Free when attached to NAT GW |
| NAT data transfer | ~$5.00 | $0.045/GB, estimated 100GB |
| S3 storage | < $1.00 | Negligible at low volume |
| VPC, subnets, SGs, IGW, RTs | $0.00 | No charge |
| **Total estimated** | **~$38** | Well within $150/month budget |

---

## Traceability Matrix

| Requirement | Component | Task |
|---|---|---|
| REQ-001 VPC Creation | networking | TASK-002 |
| REQ-002 Public Subnets | networking | TASK-002 |
| REQ-003 Private Subnets | networking | TASK-002 |
| REQ-004 Internet Gateway | networking | TASK-002 |
| REQ-005 NAT Gateway | networking | TASK-002 |
| REQ-006 Route Tables | networking | TASK-002 |
| REQ-007 Web Tier SG | security | TASK-003 |
| REQ-008 App Tier SG | security | TASK-003 |
| REQ-009 S3 Bucket | storage | TASK-004 |
| REQ-010 Remote State | root (backend.tf) | TASK-001 |
| REQ-011 Cost Constraints | all (architecture decision) | TASK-002, TASK-004 |
| REQ-012 Required Tagging | root (providers.tf) | TASK-001 |
| REQ-013 Region Constraint | root (providers.tf) | TASK-001 |
| REQ-014 Encryption | storage, root (backend.tf) | TASK-001, TASK-004 |
| REQ-015 No Hardcoded Values | all modules (variables.tf) | TASK-001 through TASK-005 |
| REQ-016 Plan Only | root (Makefile) | TASK-001 |

---

## Directory Structure

```
vpc-foundation/
+-- main.tf
+-- variables.tf
+-- outputs.tf
+-- providers.tf
+-- backend.tf
+-- terraform.tfvars.example
+-- Makefile
+-- .gitignore
+-- modules/
|   +-- networking/
|   |   +-- main.tf
|   |   +-- variables.tf
|   |   +-- outputs.tf
|   +-- security/
|   |   +-- main.tf
|   |   +-- variables.tf
|   |   +-- outputs.tf
|   +-- storage/
|       +-- main.tf
|       +-- variables.tf
|       +-- outputs.tf
+-- specs/
    +-- requirements.md
    +-- design.md
    +-- tasks.md
```
