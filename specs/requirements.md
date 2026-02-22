# Requirements Specification: vpc-foundation

## Project Summary

AWS VPC foundation infrastructure for a simple web application, deployed to eu-west-1 using Terraform. Provides networking (public/private subnets across 2 AZs, NAT gateway, internet gateway), security groups for web and application tiers, and an S3 bucket for static assets. No compute resources are provisioned; this is the foundation layer only.

---

## Functional Requirements

### REQ-001: VPC Creation

**EARS**: When the infrastructure is provisioned, the system shall create a VPC with CIDR block 10.0.0.0/16 in eu-west-1.

**Priority**: MUST

**Acceptance Criteria**:
- AC-001-1: VPC exists with CIDR 10.0.0.0/16
- AC-001-2: VPC is in eu-west-1
- AC-001-3: DNS support is enabled
- AC-001-4: DNS hostnames are enabled
- AC-001-5: VPC is tagged with Environment, Project, and Owner

**Dependencies**: None

---

### REQ-002: Public Subnets

**EARS**: When the VPC is created, the system shall create two public subnets across availability zones eu-west-1a and eu-west-1b.

**Priority**: MUST

**Acceptance Criteria**:
- AC-002-1: Public subnet in eu-west-1a exists with CIDR 10.0.1.0/24
- AC-002-2: Public subnet in eu-west-1b exists with CIDR 10.0.2.0/24
- AC-002-3: Both subnets have map_public_ip_on_launch enabled
- AC-002-4: Both subnets are tagged with Environment, Project, and Owner

**Dependencies**: REQ-001

---

### REQ-003: Private Subnets

**EARS**: When the VPC is created, the system shall create two private subnets across availability zones eu-west-1a and eu-west-1b.

**Priority**: MUST

**Acceptance Criteria**:
- AC-003-1: Private subnet in eu-west-1a exists with CIDR 10.0.10.0/24
- AC-003-2: Private subnet in eu-west-1b exists with CIDR 10.0.20.0/24
- AC-003-3: Neither subnet has map_public_ip_on_launch enabled
- AC-003-4: Both subnets are tagged with Environment, Project, and Owner

**Dependencies**: REQ-001

---

### REQ-004: Internet Gateway

**EARS**: When the VPC is created, the system shall attach an internet gateway to enable outbound internet access from public subnets.

**Priority**: MUST

**Acceptance Criteria**:
- AC-004-1: Internet gateway exists and is attached to the VPC
- AC-004-2: Internet gateway is tagged with Environment, Project, and Owner

**Dependencies**: REQ-001

---

### REQ-005: NAT Gateway

**EARS**: When the VPC is created, the system shall provision a NAT gateway in a public subnet to enable outbound internet access from private subnets.

**Priority**: MUST

**Acceptance Criteria**:
- AC-005-1: NAT gateway exists in one of the public subnets
- AC-005-2: NAT gateway has an allocated Elastic IP
- AC-005-3: NAT gateway is tagged with Environment, Project, and Owner

**Dependencies**: REQ-002

---

### REQ-006: Route Tables

**EARS**: When subnets are created, the system shall configure route tables so that public subnets route 0.0.0.0/0 through the internet gateway and private subnets route 0.0.0.0/0 through the NAT gateway.

**Priority**: MUST

**Acceptance Criteria**:
- AC-006-1: Public route table has a route for 0.0.0.0/0 via the internet gateway
- AC-006-2: Public route table is associated with both public subnets
- AC-006-3: Private route table has a route for 0.0.0.0/0 via the NAT gateway
- AC-006-4: Private route table is associated with both private subnets
- AC-006-5: All route tables are tagged with Environment, Project, and Owner

**Dependencies**: REQ-002, REQ-003, REQ-004, REQ-005

---

### REQ-007: Web Tier Security Group

**EARS**: When the VPC is created, the system shall create a security group allowing inbound HTTP (port 80) and HTTPS (port 443) traffic from 0.0.0.0/0.

**Priority**: MUST

**Acceptance Criteria**:
- AC-007-1: Security group exists in the VPC
- AC-007-2: Ingress rule allows TCP port 80 from 0.0.0.0/0
- AC-007-3: Ingress rule allows TCP port 443 from 0.0.0.0/0
- AC-007-4: Egress rule allows all outbound traffic
- AC-007-5: Security group is tagged with Environment, Project, and Owner

**Dependencies**: REQ-001

---

### REQ-008: Application Tier Security Group

**EARS**: When the VPC is created, the system shall create a security group allowing inbound traffic only from the web tier security group.

**Priority**: MUST

**Acceptance Criteria**:
- AC-008-1: Security group exists in the VPC
- AC-008-2: Ingress rule allows traffic from the web tier security group only
- AC-008-3: No ingress rule allows traffic from 0.0.0.0/0
- AC-008-4: Egress rule allows all outbound traffic
- AC-008-5: Security group is tagged with Environment, Project, and Owner

**Dependencies**: REQ-001, REQ-007

---

### REQ-009: S3 Bucket for Static Assets

**EARS**: When the infrastructure is provisioned, the system shall create an S3 bucket for static assets with versioning enabled.

**Priority**: MUST

**Acceptance Criteria**:
- AC-009-1: S3 bucket exists with name derived from a configurable variable
- AC-009-2: Versioning is enabled on the bucket
- AC-009-3: Server-side encryption (AES256) is enabled by default
- AC-009-4: Public access is blocked (all four block public access settings are true)
- AC-009-5: Bucket is tagged with Environment, Project, and Owner

**Dependencies**: None

---

### REQ-010: Remote State Backend

**EARS**: When the Terraform configuration is initialised, the system shall store state in an S3 backend with DynamoDB locking.

**Priority**: MUST

**Acceptance Criteria**:
- AC-010-1: Backend is configured as S3 with a specified bucket, key, and region
- AC-010-2: DynamoDB table is specified for state locking
- AC-010-3: Backend encryption is enabled
- AC-010-4: Backend bucket has versioning enabled

**Dependencies**: None

---

## Non-Functional Requirements

### REQ-011: Cost Constraints

**EARS**: The infrastructure shall not exceed $150/month in estimated running cost.

**Priority**: MUST

**Acceptance Criteria**:
- AC-011-1: NAT gateway is single-AZ (estimated ~$32/month)
- AC-011-2: No compute instances are provisioned
- AC-011-3: Maximum allowed instance size (for future use) is t3.large, enforced as a variable constraint
- AC-011-4: Terraform plan output contains no resources exceeding the cost envelope

**Dependencies**: None

**Notes**: Primary cost drivers are NAT gateway (~$32/month fixed + data transfer) and S3 storage (negligible at low volume). Total estimated baseline cost is approximately $35-40/month.

---

### REQ-012: Required Tagging

**EARS**: Every resource that supports tags shall be tagged with Environment, Project, and Owner.

**Priority**: MUST

**Acceptance Criteria**:
- AC-012-1: Provider default_tags block includes Environment, Project, Owner, and ManagedBy
- AC-012-2: All resources in the Terraform plan carry these tags

**Dependencies**: None

---

### REQ-013: Region Constraint

**EARS**: All resources shall be deployed exclusively in eu-west-1.

**Priority**: MUST

**Acceptance Criteria**:
- AC-013-1: Provider region is set to eu-west-1
- AC-013-2: No resource specifies a region other than eu-west-1
- AC-013-3: Region is a variable with default eu-west-1

**Dependencies**: None

---

### REQ-014: Encryption

**EARS**: The S3 bucket for static assets and the Terraform state bucket shall have server-side encryption enabled.

**Priority**: MUST

**Acceptance Criteria**:
- AC-014-1: Static assets S3 bucket has SSE-S3 (AES256) default encryption
- AC-014-2: Terraform state backend configuration specifies encrypt = true

**Dependencies**: REQ-009, REQ-010

---

### REQ-015: No Hardcoded Environment Values

**EARS**: Region, availability zones, CIDR blocks, instance size limits, S3 bucket names, and tag values shall be configurable via Terraform variables with descriptions.

**Priority**: MUST

**Acceptance Criteria**:
- AC-015-1: Every environment-specific value is a Terraform variable
- AC-015-2: Every variable has a description attribute
- AC-015-3: Defaults are provided for region (eu-west-1), AZs, and CIDR blocks

**Dependencies**: None

---

### REQ-016: Terraform Plan Only

**EARS**: The build pipeline shall terminate at terraform plan. No apply or destroy targets shall exist.

**Priority**: MUST

**Acceptance Criteria**:
- AC-016-1: Makefile contains init, validate, plan targets
- AC-016-2: Makefile does not contain apply or destroy targets

**Dependencies**: None

---

## Future Considerations (Not In Scope)

- Auto-scaling groups for compute (noted for future builds)
- Multi-NAT gateway for high availability (single NAT gateway chosen for cost)
- VPC flow logs (can be added when compute is provisioned)
- IAM roles for compute instances
