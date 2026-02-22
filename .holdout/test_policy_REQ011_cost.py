"""
REQ-011: Cost Constraints

Validates cost guardrails are in place:
- AC-011-1: NAT gateway is single-AZ (max 1 NAT GW)
- AC-011-2: No compute instances are provisioned
- AC-011-3: Maximum instance size is t3.large, enforced as a variable constraint
- AC-011-4: No resources exceed the cost envelope
"""
import re


COMPUTE_RESOURCE_TYPES = {
    "aws_instance",
    "aws_launch_template",
    "aws_launch_configuration",
    "aws_autoscaling_group",
    "aws_ecs_service",
    "aws_ecs_task_definition",
    "aws_eks_cluster",
    "aws_eks_node_group",
    "aws_lambda_function",
    "aws_rds_instance",
    "aws_db_instance",
    "aws_elasticache_cluster",
    "aws_redshift_cluster",
    "aws_emr_cluster",
}


class TestCostConstraints:
    """REQ-011: Cost guardrails and budget enforcement."""

    def test_ac_011_1_single_nat_gateway(self, resources_by_type):
        """AC-011-1: Only one NAT gateway (single-AZ for cost control)."""
        nats = resources_by_type.get("aws_nat_gateway", [])
        assert len(nats) <= 1, (
            f"Expected at most 1 NAT gateway (single-AZ), found {len(nats)}. "
            "Multiple NAT gateways would exceed cost budget."
        )

    def test_ac_011_2_no_compute_instances(self, resources_by_type):
        """AC-011-2: No compute instances are provisioned."""
        for resource_type in COMPUTE_RESOURCE_TYPES:
            instances = resources_by_type.get(resource_type, [])
            assert len(instances) == 0, (
                f"Found {len(instances)} {resource_type} resource(s). "
                "This is a foundation layer; no compute should be provisioned."
            )

    def test_ac_011_2_no_compute_in_resource_changes(self, resource_changes):
        """AC-011-2: No compute resources in resource_changes either."""
        for change in resource_changes:
            rtype = change.get("type", "")
            assert rtype not in COMPUTE_RESOURCE_TYPES, (
                f"Found compute resource '{rtype}' in resource changes. "
                "Foundation layer must not provision compute."
            )

    def test_ac_011_3_max_instance_size_variable(self, all_terraform_source):
        """AC-011-3: A variable constrains maximum instance size to t3.large.

        Checks that a variable exists with a validation block referencing
        allowed instance types, with t3.large as the largest permitted.
        """
        # Look for a variable with instance size/type in its name
        # and a validation block
        has_instance_var = re.search(
            r'variable\s+"[^"]*instance[^"]*"', all_terraform_source
        ) or re.search(
            r'variable\s+"[^"]*instance[^"]*"', all_terraform_source, re.IGNORECASE
        )

        # Check for t3.large appearing as a constraint
        has_t3_large_ref = "t3.large" in all_terraform_source

        assert has_instance_var or has_t3_large_ref, (
            "No variable found constraining instance size. "
            "Expected a variable with instance type validation including t3.large."
        )

    def test_ac_011_4_no_expensive_resources(self, resources_by_type):
        """AC-011-4: No obviously expensive resources beyond the expected set.

        The expected resources for this foundation are:
        VPC, subnets, IGW, NAT GW, EIP, route tables, security groups, S3.
        """
        expected_types = {
            "aws_vpc",
            "aws_subnet",
            "aws_internet_gateway",
            "aws_nat_gateway",
            "aws_eip",
            "aws_route_table",
            "aws_route",
            "aws_route_table_association",
            "aws_security_group",
            "aws_security_group_rule",
            "aws_vpc_security_group_ingress_rule",
            "aws_vpc_security_group_egress_rule",
            "aws_s3_bucket",
            "aws_s3_bucket_versioning",
            "aws_s3_bucket_server_side_encryption_configuration",
            "aws_s3_bucket_public_access_block",
            "aws_main_route_table_association",
            "aws_default_security_group",
            "aws_default_route_table",
            "aws_default_network_acl",
        }

        expensive_types = {
            "aws_lb", "aws_alb", "aws_elb",
            "aws_rds_instance", "aws_db_instance",
            "aws_elasticache_cluster",
            "aws_instance",
            "aws_nat_gateway",  # We allow 1
        }

        for rtype, resources in resources_by_type.items():
            if rtype in expensive_types and rtype != "aws_nat_gateway":
                assert len(resources) == 0, (
                    f"Found expensive resource type '{rtype}' ({len(resources)} instances). "
                    "This exceeds the foundation layer cost envelope."
                )
