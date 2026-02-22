# Cost Report: vpc-foundation

**Analyst**: Cost Agent
**Date**: 2026-02-22

## Verdict: PASS

## Monthly Cost Estimate

| Resource | Monthly Cost (USD) | Notes |
|---|---|---|
| NAT Gateway (fixed) | $32.40 | $0.045/hr x 720 hrs, single-AZ in eu-west-1a |
| NAT Gateway (data transfer) | $0 - $5 | $0.045/GB processed; foundation-only, no compute generating traffic |
| Elastic IP (attached) | $0.00 | Free while attached to running NAT Gateway |
| S3 Bucket (static assets) | < $1 | Storage + versioning at low volume is negligible |
| VPC | $0.00 | No charge |
| Subnets (x4) | $0.00 | No charge |
| Internet Gateway | $0.00 | No charge |
| Route Tables (x2) | $0.00 | No charge |
| Security Groups (x2) | $0.00 | No charge |
| **Total** | **~$33 - $38** | Baseline with minimal data transfer |

## Budget Compliance

- Budget: $150/month
- Estimated: ~$33 - $38/month
- Headroom: ~$112 - $117/month (75-78% of budget unused)
- Status: **WITHIN BUDGET**

## Guardrail Compliance

| Check | Status | Notes |
|---|---|---|
| Budget compliance | PASS | ~$33-38/month against $150/month ceiling |
| Instance sizing | PASS | No compute instances provisioned. `max_instance_size` variable set to `t3.large` as advisory guardrail for future use. |
| Auto-scaling bounds | N/A | No ASGs; foundation-only build |
| Storage lifecycle | ADVISORY | S3 versioning enabled but no lifecycle rules configured (see findings) |
| Data transfer | PASS | Single NAT Gateway; no compute generating cross-AZ or outbound traffic at present |
| Reserved/Spot eligibility | N/A | No compute resources |
| Idle resource risk | LOW | NAT Gateway incurs fixed cost (~$32/month) regardless of traffic; acceptable given single-AZ design choice |
| Missing cost tags | PASS | `default_tags` in provider block applies Environment, Project, Owner, ManagedBy to all resources |
| Database right-sizing | N/A | No databases |
| Network architecture | PASS | Single NAT Gateway is an explicit cost-driven design decision per REQ-005 and design spec |

## Findings

### Critical

None.

### High

None.

### Medium

**M1: S3 versioning enabled without lifecycle rules**

The static assets bucket (`modules/storage/main.tf`) has versioning enabled per REQ-009 but no `aws_s3_bucket_lifecycle_configuration` resource exists. Over time, old object versions accumulate and storage costs grow without bound. For a foundation build with minimal storage this is not urgent, but it should be addressed before the bucket sees significant write traffic.

Recommendation: Add a lifecycle rule to expire non-current versions after 30-90 days, or to transition them to S3 Glacier after a retention period. This prevents unbounded version accumulation.

### Low

**L1: NAT Gateway runs at full cost with zero traffic**

The NAT Gateway costs ~$32/month whether or not any private subnet traffic uses it. Since no compute is provisioned in this foundation build, the NAT Gateway is currently idle. This is an expected consequence of provisioning the foundation ahead of the application tier and is documented in the design spec. The cost is acceptable within the budget envelope.

If the foundation will sit idle for an extended period before compute is added, consider deferring NAT Gateway provisioning to the compute build phase.

**L2: Elastic IP pricing change (Feb 2024)**

AWS began charging $3.60/month for all public IPv4 addresses in February 2024. However, EIPs attached to a running NAT Gateway remain free as part of the NAT Gateway's pricing. The EIP here (`aws_eip.nat`) is attached via `allocation_id` in the NAT Gateway resource, so no additional charge applies. This is correct as implemented. The risk would materialise only if the NAT Gateway were destroyed while the EIP remained allocated.

## Architecture-Level Cost Assessment

The architecture is well-designed for cost control. The dominant cost decision, using a single NAT Gateway rather than one per AZ, is explicitly documented in both requirements (REQ-005, AC-005-1: "exists in one of the public subnets") and design ("single-AZ for cost"). This trades availability for cost, reducing NAT Gateway spend from ~$65/month (two gateways) to ~$32/month. The trade-off is appropriate for a dev/staging foundation where private subnet availability during an AZ failure is an acceptable risk.

The total estimated baseline of ~$33-38/month uses roughly 25% of the $150/month budget, leaving substantial headroom for future compute, load balancers, and data transfer when the application tier is added.

All resources that support tags carry the four mandatory tags via the provider `default_tags` block, enabling reliable cost attribution via AWS Cost Explorer.

No resources have unbounded scaling characteristics. The `max_instance_size` variable (`t3.large`) serves as an advisory guardrail for future builds, though it is not enforced programmatically at this stage.

## Recommendations

1. **Add S3 lifecycle rules** before the bucket sees production traffic. Expire non-current versions after 30-90 days to prevent unbounded storage growth.
2. **Consider deferring NAT Gateway** if the foundation will be idle for more than a month before compute is provisioned. The ~$32/month fixed cost provides no value until private subnet instances need outbound internet access.
3. **Enforce `max_instance_size` programmatically** in the compute build phase. The variable exists but is not validated against actual instance types. A `validation` block on the variable, or a Sentinel/OPA policy, would make this a hard constraint rather than an advisory one.
4. **Add VPC endpoints** for S3 (gateway endpoint, free) when compute is provisioned. This routes S3 traffic through the AWS backbone rather than the NAT Gateway, reducing both data transfer costs and latency.
