# Security Report: vpc-foundation

**Analyst**: Security Agent
**Date**: 2026-02-22

## Verdict: PASS WITH FINDINGS

## Threat Model

**System scope**: A foundation-only VPC build in AWS eu-west-1 provisioning networking (VPC, subnets, gateways, route tables), security groups (web and application tiers), and an S3 bucket for static assets. No compute, no IAM roles, no databases. Terraform state is stored remotely in S3 with DynamoDB locking.

**Attack surface**:

- **Network layer**: Internet Gateway exposes public subnets. Web security group opens ports 80/443 to the internet (by design). App security group accepts traffic from the web SG. NAT gateway provides outbound-only access from private subnets.
- **Storage layer**: S3 bucket for static assets. Public access blocked. Encryption at rest via SSE-S3 (AES256).
- **State layer**: Terraform state in S3 with encryption and DynamoDB locking. State file will contain all resource IDs and configuration once applied.
- **Control plane**: AWS API access. No IAM resources defined in this build; credentials are assumed to be provided externally (environment variables or instance profile).

**Trust boundaries**:

1. Internet to VPC (via IGW, filtered by web SG)
2. Web tier to application tier (filtered by app SG)
3. Private subnets to internet (outbound only, via NAT GW)
4. Terraform operator to AWS API (out of scope for this build)
5. S3 bucket access (no bucket policy; relies on IAM identity policies and public access block)

## Findings

### Critical

None.

### High

None.

### Medium

**M-1: VPC Flow Logs not enabled** (CWE-778)

VPC flow logs are not configured. Without flow logs, there is no record of accepted or rejected network traffic within the VPC. This limits the ability to detect reconnaissance, lateral movement, or data exfiltration once compute resources are added.

- **File**: `modules/networking/main.tf`
- **Risk**: No network-level audit trail. Incident investigation and anomaly detection are not possible at the VPC layer.
- **Mitigation**: Add an `aws_flow_log` resource capturing all traffic to CloudWatch Logs or S3. The requirements document notes this as a future consideration (REQ-FUT), so the omission is deliberate, but it should be addressed before any compute is deployed.

**M-2: App security group allows all protocols and ports from web SG** (CWE-284)

The app security group ingress rule uses `ip_protocol = "-1"` (all traffic) from the web security group. This is more permissive than necessary. When compute is deployed, the app tier will accept any protocol and any port from the web tier, not just the application port(s).

- **File**: `modules/security/main.tf`, line 43-47
- **Resource**: `aws_vpc_security_group_ingress_rule.app_from_web`
- **Risk**: Overly broad access. If the web tier is compromised, the attacker has unrestricted network access to the application tier rather than being constrained to specific ports.
- **Mitigation**: Restrict to the specific port(s) the application will listen on (e.g., TCP 8080, TCP 443). Since no compute exists yet, this can be tightened when the application port is known, but the current default is unnecessarily permissive.

### Low

**L-1: S3 bucket has no bucket policy enforcing TLS-only access** (CWE-319)

The S3 bucket has public access blocked and encryption at rest, but no bucket policy requiring `aws:SecureTransport`. While AWS SDKs and the console use HTTPS by default, an explicit policy ensures that no client can access the bucket over unencrypted HTTP.

- **File**: `modules/storage/main.tf`
- **Risk**: Without an explicit TLS enforcement policy, a misconfigured client or tool could theoretically access objects over HTTP within the AWS network.
- **Mitigation**: Add an `aws_s3_bucket_policy` with a `Deny` statement for `"Bool": {"aws:SecureTransport": "false"}`.

**L-2: No variable validation on CIDR inputs** (CWE-20)

The `vpc_cidr`, `public_subnet_cidrs`, and `private_subnet_cidrs` variables accept arbitrary strings without validation. An operator could supply an invalid CIDR (e.g., overlapping ranges, non-RFC 1918 addresses, or malformed input) and Terraform would only catch this at plan/apply time via AWS API errors.

- **File**: `variables.tf` (root), `modules/networking/variables.tf`
- **Risk**: Configuration error leading to unexpected network topology. Minimal real-world risk since Terraform plan would surface the issue before apply.
- **Mitigation**: Add `validation` blocks to CIDR variables using `can(cidrhost(var.vpc_cidr, 0))` to catch malformed input early.

**L-3: Terraform state backend bucket security is assumed, not enforced** (CWE-284)

The `backend.tf` references `vpc-foundation-tfstate` and `vpc-foundation-tflock` as pre-existing resources. Their security configuration (versioning, public access block, encryption, DynamoDB capacity) is not managed or validated by this build. A misconfigured state bucket could expose sensitive state data.

- **File**: `backend.tf`
- **Risk**: State files contain all resource identifiers, configuration values, and potentially sensitive outputs. If the state bucket is misconfigured (e.g., public, unversioned), this data is exposed.
- **Mitigation**: Document the required configuration for the state backend bucket. Consider a separate bootstrap Terraform configuration that provisions the state backend with verified security settings.

### Informational

**I-1: Public subnets auto-assign public IPs** (CWE-284)

Both public subnets have `map_public_ip_on_launch = true`. This is correct for the intended use case (web-facing load balancers) and is specified in REQ-002. However, any EC2 instance launched into these subnets will automatically receive a public IP, regardless of whether one is needed. When compute is added, instances should be placed in private subnets, with only load balancers in public subnets.

**I-2: Single NAT gateway creates an availability risk**

The NAT gateway is deployed only in eu-west-1a. If that AZ experiences an outage, private subnet instances in eu-west-1b lose outbound internet access. This is a deliberate cost decision (REQ-011, AC-011-1) and is documented in the design. Note for future builds: if availability requirements increase, deploy a NAT gateway per AZ.

**I-3: No S3 access logging configured**

The static assets S3 bucket does not have server access logging enabled. Access logging provides an audit trail of requests made to the bucket. This is low priority for a foundation build with no data, but should be enabled when the bucket is used in production.

**I-4: Makefile uses `-backend=false` for init**

The `init` target uses `-backend=false`, which means `terraform init` does not connect to the remote backend. This is appropriate for validation-only pipelines (REQ-016) but means that state locking and remote state features are not exercised during the build process. No security concern, but worth noting for operational clarity.

**I-5: SSE-S3 (AES256) used rather than SSE-KMS**

The S3 bucket uses AWS-managed keys (SSE-S3) rather than KMS. SSE-S3 is adequate for most use cases, but SSE-KMS provides additional controls: key rotation management, CloudTrail logging of key usage, and the ability to restrict access via key policies. For a foundation build, SSE-S3 is reasonable. For production workloads with compliance requirements, consider upgrading to SSE-KMS.

## Checklist Results

| Check | CWE | Result | Notes |
|---|---|---|---|
| Overly permissive IAM | CWE-269 | **N/A** | No IAM resources in this build |
| Exposed ports | CWE-284 | **PASS** | Web SG: 80/443 from 0.0.0.0/0 (by design, per REQ-007). App SG: from web SG only. No SSH, RDP, or database ports exposed. |
| Missing encryption at rest | CWE-311 | **PASS** | S3 bucket has SSE-S3 (AES256). State backend has `encrypt = true`. |
| Missing encryption in transit | CWE-319 | **PASS (with finding L-1)** | No HTTP listeners (no compute). S3 lacks explicit TLS enforcement policy. |
| Hardcoded secrets | CWE-798 | **PASS** | No credentials, keys, or secrets in any .tf file. `.gitignore` excludes `*.tfvars`. |
| Public S3 buckets | CWE-284 | **PASS** | All four `block_public_access` settings are `true`. No `acl` argument. |
| Missing audit logging | CWE-778 | **FAIL (finding M-1)** | No VPC flow logs. No S3 access logging. |
| Network isolation | CWE-284 | **PASS** | Private subnets correctly routed via NAT GW (outbound only). Public subnets routed via IGW. Route table associations are correct. |
| Instance metadata v1 | CWE-918 | **N/A** | No EC2 instances in this build |

## Summary

The vpc-foundation build has a sound security posture for a foundation-only layer. No critical or high-severity findings. The code follows infrastructure security best practices: public access is blocked on S3, encryption at rest is enabled, security groups use standalone rules with appropriate segmentation, state is encrypted with locking, and no credentials are hardcoded.

Two medium findings should be addressed before compute resources are deployed on this foundation: enabling VPC flow logs (M-1) and tightening the app security group to specific ports (M-2). The low findings (TLS enforcement policy on S3, input validation, state backend documentation) represent hardening opportunities rather than immediate risks.

The build is suitable for deployment as a foundation layer. The security gaps identified are expected for a pre-compute infrastructure skeleton and are all resolvable without architectural changes.
