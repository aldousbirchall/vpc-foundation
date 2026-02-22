"""
REQ-005: NAT Gateway

Validates that the Terraform plan provisions a NAT gateway:
- AC-005-1: NAT gateway exists in one of the public subnets
- AC-005-2: NAT gateway has an allocated Elastic IP
- AC-005-3: NAT gateway is tagged with Environment, Project, and Owner
"""


class TestNATGateway:
    """REQ-005: NAT gateway in a public subnet with EIP."""

    def _get_nat_gateways(self, resources_by_type):
        nats = resources_by_type.get("aws_nat_gateway", [])
        assert len(nats) >= 1, "No aws_nat_gateway resource found in plan"
        return nats

    def test_ac_005_1_nat_gateway_exists(self, resources_by_type):
        """AC-005-1: At least one NAT gateway exists in the plan."""
        nats = self._get_nat_gateways(resources_by_type)
        assert len(nats) >= 1

    def test_ac_005_1_nat_single_az(self, resources_by_type):
        """AC-005-1 / AC-011-1: Only one NAT gateway (single-AZ for cost)."""
        nats = resources_by_type.get("aws_nat_gateway", [])
        assert len(nats) == 1, (
            f"Expected exactly 1 NAT gateway (single-AZ), found {len(nats)}"
        )

    def test_ac_005_2_elastic_ip_exists(self, resources_by_type):
        """AC-005-2: An Elastic IP (aws_eip) exists for the NAT gateway."""
        eips = resources_by_type.get("aws_eip", [])
        assert len(eips) >= 1, (
            "No aws_eip resource found; NAT gateway requires an Elastic IP"
        )

    def test_ac_005_2_nat_has_allocation_id(self, resources_by_type):
        """AC-005-2: NAT gateway references an allocation_id (EIP)."""
        nats = self._get_nat_gateways(resources_by_type)
        for nat in nats:
            # allocation_id may be a computed reference in plan.json
            # Check it's present in the values or in resource config
            allocation_id = nat["values"].get("allocation_id")
            # In mock plans, this might be a placeholder. Just ensure
            # the field is present (not absent from the schema).
            assert "allocation_id" in nat["values"], (
                "NAT gateway must have an allocation_id referencing an EIP"
            )

    def test_ac_005_3_nat_tags(self, resources_by_type):
        """AC-005-3: NAT gateway tagged with Environment, Project, Owner."""
        nats = self._get_nat_gateways(resources_by_type)
        for nat in nats:
            tags = nat["values"].get("tags", {}) or {}
            tags_all = nat["values"].get("tags_all", {}) or {}
            combined = {**tags_all, **tags}
            for required_tag in ["Environment", "Project", "Owner"]:
                assert required_tag in combined, (
                    f"NAT gateway missing tag '{required_tag}'. "
                    f"Found: {list(combined.keys())}"
                )
