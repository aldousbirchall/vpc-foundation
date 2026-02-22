# Task Specification: vpc-foundation

## Task Dependency Graph

```
TASK-001 (Scaffolding)
    |
    +---> TASK-002 (Networking)
    |         |
    |         +---> TASK-003 (Security)
    |         |
    |         +---> TASK-004 (Storage) [no dependency on TASK-002, but sequenced after]
    |
    +---> TASK-004 (Storage)
    |
    +---> TASK-005 (Root Composition) [depends on TASK-002, TASK-003, TASK-004]
```

TASK-001 -> TASK-002 -> TASK-003 -> TASK-005
TASK-001 -> TASK-004 -> TASK-005

---

## TASK-001: Scaffolding

**Objective**: Create the project skeleton with provider configuration, backend configuration, Makefile, .gitignore, and root variable definitions.

**Dependencies**: None

**Requirements Covered**: REQ-010, REQ-012, REQ-013, REQ-015, REQ-016

**Deliverables**:

| File | Contents |
|---|---|
| `src/providers.tf` | Terraform and AWS provider blocks with required_version >= 1.5.0, AWS provider ~> 5.0, region variable, default_tags block (Environment, Project, Owner, ManagedBy) |
| `src/backend.tf` | S3 backend configuration with bucket, key, region, encrypt, dynamodb_table |
| `src/variables.tf` | Root-level variables: region, environment, project, owner, vpc_cidr, public_subnet_cidrs, private_subnet_cidrs, availability_zones, bucket_name, max_instance_size. All with type, default (where applicable), and description. |
| `src/outputs.tf` | Empty file (populated in TASK-005) |
| `src/main.tf` | Empty file (populated in TASK-005) |
| `src/terraform.tfvars.example` | Example variable values for local use |
| `src/Makefile` | Targets: init, fmt, validate, plan. No apply or destroy targets. |
| `src/.gitignore` | Terraform patterns: .terraform/, *.tfstate, *.tfstate.backup, .terraform.lock.hcl, *.tfvars (not .tfvars.example) |
| `src/modules/` | Empty directory structure: networking/, security/, storage/ |

**Acceptance Criteria**:
- `terraform fmt -check` passes on all .tf files
- `terraform validate` passes (after init with backend disabled)
- Makefile contains init, fmt, validate, plan targets
- Makefile does not contain apply or destroy targets
- Every variable in variables.tf has a description
- default_tags includes Environment, Project, Owner, ManagedBy
- .gitignore excludes .terraform/, *.tfstate, *.tfvars

---

## TASK-002: Networking Module

**Objective**: Implement the networking module: VPC, subnets, internet gateway, NAT gateway, Elastic IP, route tables, and route table associations.

**Dependencies**: TASK-001

**Requirements Covered**: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-011, REQ-015

**Deliverables**:

| File | Contents |
|---|---|
| `src/modules/networking/main.tf` | All networking resources as specified in design.md |
| `src/modules/networking/variables.tf` | vpc_cidr, public_subnet_cidrs, private_subnet_cidrs, availability_zones, environment, project. All with type, default, description. |
| `src/modules/networking/outputs.tf` | vpc_id, public_subnet_ids, private_subnet_ids, nat_gateway_id, internet_gateway_id |

**Resources to Create**:
1. `aws_vpc` - CIDR 10.0.0.0/16, enable_dns_support = true, enable_dns_hostnames = true
2. `aws_subnet` (public x2) - map_public_ip_on_launch = true, CIDRs and AZs from variables
3. `aws_subnet` (private x2) - map_public_ip_on_launch = false
4. `aws_internet_gateway` - attached to VPC
5. `aws_eip` - domain = "vpc", for NAT gateway
6. `aws_nat_gateway` - in first public subnet, uses the EIP
7. `aws_route_table` (public) - route 0.0.0.0/0 to IGW
8. `aws_route_table` (private) - route 0.0.0.0/0 to NAT GW
9. `aws_route_table_association` (x4) - public subnets to public RT, private subnets to private RT

**Naming Convention**: Each resource gets a Name tag following `{project}-{environment}-{resource}` pattern using `var.project` and `var.environment`.

**Acceptance Criteria**:
- `terraform fmt -check` passes
- `terraform validate` passes (module in isolation with mock provider)
- VPC CIDR is from variable, defaults to 10.0.0.0/16
- Two public subnets across two AZs with public IP mapping enabled
- Two private subnets across two AZs without public IP mapping
- IGW attached to VPC
- NAT GW in first public subnet with EIP
- Public route table routes 0.0.0.0/0 to IGW, associated with both public subnets
- Private route table routes 0.0.0.0/0 to NAT GW, associated with both private subnets
- All resources have Name tags following naming convention
- NAT gateway is single-AZ (cost constraint)
- All outputs are defined and reference the correct resources

---

## TASK-003: Security Module

**Objective**: Implement the security module: web tier and application tier security groups with standalone rules.

**Dependencies**: TASK-002 (requires VPC ID output)

**Requirements Covered**: REQ-007, REQ-008, REQ-015

**Deliverables**:

| File | Contents |
|---|---|
| `src/modules/security/main.tf` | Security groups and standalone rules as specified in design.md |
| `src/modules/security/variables.tf` | vpc_id, environment, project. All with type and description. |
| `src/modules/security/outputs.tf` | web_security_group_id, app_security_group_id |

**Resources to Create**:
1. `aws_security_group` (web) - in VPC, name following convention
2. `aws_vpc_security_group_ingress_rule` (HTTP) - port 80, TCP, 0.0.0.0/0
3. `aws_vpc_security_group_ingress_rule` (HTTPS) - port 443, TCP, 0.0.0.0/0
4. `aws_vpc_security_group_egress_rule` (web) - all traffic
5. `aws_security_group` (app) - in VPC, name following convention
6. `aws_vpc_security_group_ingress_rule` (app from web) - all ports, source = web SG ID
7. `aws_vpc_security_group_egress_rule` (app) - all traffic

**Acceptance Criteria**:
- `terraform fmt -check` passes
- `terraform validate` passes
- Web SG allows TCP 80 and TCP 443 from 0.0.0.0/0
- Web SG allows all egress
- App SG allows ingress only from web SG (referenced by security group ID)
- App SG has no ingress rule with cidr_ipv4 = "0.0.0.0/0"
- App SG allows all egress
- Uses standalone rule resources, not inline ingress/egress blocks
- All resources have Name tags following naming convention
- All outputs are defined

---

## TASK-004: Storage Module

**Objective**: Implement the storage module: S3 bucket with versioning, encryption, and public access block.

**Dependencies**: TASK-001

**Requirements Covered**: REQ-009, REQ-014, REQ-015

**Deliverables**:

| File | Contents |
|---|---|
| `src/modules/storage/main.tf` | S3 bucket and associated configuration resources |
| `src/modules/storage/variables.tf` | bucket_name, environment, project. All with type and description. |
| `src/modules/storage/outputs.tf` | bucket_id, bucket_arn |

**Resources to Create**:
1. `aws_s3_bucket` - name from variable
2. `aws_s3_bucket_versioning` - status = "Enabled"
3. `aws_s3_bucket_server_side_encryption_configuration` - AES256
4. `aws_s3_bucket_public_access_block` - all four settings = true

**Acceptance Criteria**:
- `terraform fmt -check` passes
- `terraform validate` passes
- Bucket name comes from a variable (no hardcoded name)
- Versioning is enabled
- Server-side encryption is AES256
- All four public access block settings are true (block_public_acls, block_public_policy, ignore_public_acls, restrict_public_buckets)
- Bucket has no bucket policy (access controlled by block only)
- All outputs are defined

---

## TASK-005: Root Module Composition

**Objective**: Wire all modules together in the root main.tf, define all outputs, and create terraform.tfvars.example.

**Dependencies**: TASK-002, TASK-003, TASK-004

**Requirements Covered**: REQ-011, REQ-012, REQ-015

**Deliverables**:

| File | Contents |
|---|---|
| `src/main.tf` | Module blocks for networking, security, storage. Pass variables through. |
| `src/outputs.tf` | All module outputs re-exported: vpc_id, public_subnet_ids, private_subnet_ids, nat_gateway_id, internet_gateway_id, web_security_group_id, app_security_group_id, bucket_id, bucket_arn |
| `src/terraform.tfvars.example` | Example values for all required variables (owner, bucket_name) and optional overrides |

**Module Wiring**:
```hcl
module "networking" {
  source              = "./modules/networking"
  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones  = var.availability_zones
  environment         = var.environment
  project             = var.project
}

module "security" {
  source      = "./modules/security"
  vpc_id      = module.networking.vpc_id
  environment = var.environment
  project     = var.project
}

module "storage" {
  source      = "./modules/storage"
  bucket_name = var.bucket_name
  environment = var.environment
  project     = var.project
}
```

**Acceptance Criteria**:
- `terraform fmt -check` passes on all files
- `terraform validate` passes (with backend config disabled)
- All three modules are referenced in main.tf
- Module security receives vpc_id from module networking
- All module outputs are re-exported in root outputs.tf
- terraform.tfvars.example contains all required variables with placeholder values
- No apply or destroy targets in Makefile (verify from TASK-001)
- Full `terraform plan` runs without error (with valid AWS credentials and backend)
