"""
REQ-001: VPC Creation

Validates that the Terraform plan creates a VPC with the required properties:
- AC-001-1: VPC exists with CIDR 10.0.0.0/16
- AC-001-3: DNS support is enabled
- AC-001-4: DNS hostnames are enabled
- AC-001-5: VPC is tagged with Environment, Project, and Owner
"""


class TestVPCCreation:
    """REQ-001: VPC exists with correct CIDR, DNS settings, and tags."""

    def _get_vpcs(self, resources_by_type):
        vpcs = resources_by_type.get("aws_vpc", [])
        assert len(vpcs) >= 1, "No aws_vpc resource found in plan"
        return vpcs

    def test_ac_001_1_vpc_cidr(self, resources_by_type):
        """AC-001-1: VPC exists with CIDR 10.0.0.0/16."""
        vpcs = self._get_vpcs(resources_by_type)
        cidr_blocks = [v["values"].get("cidr_block") for v in vpcs]
        assert "10.0.0.0/16" in cidr_blocks, (
            f"Expected VPC with CIDR 10.0.0.0/16, found: {cidr_blocks}"
        )

    def test_ac_001_3_dns_support(self, resources_by_type):
        """AC-001-3: DNS support is enabled on the VPC."""
        vpcs = self._get_vpcs(resources_by_type)
        main_vpc = [v for v in vpcs if v["values"].get("cidr_block") == "10.0.0.0/16"]
        assert len(main_vpc) == 1, "Expected exactly one VPC with CIDR 10.0.0.0/16"
        values = main_vpc[0]["values"]
        assert values.get("enable_dns_support") is True, (
            "DNS support must be enabled on the VPC"
        )

    def test_ac_001_4_dns_hostnames(self, resources_by_type):
        """AC-001-4: DNS hostnames are enabled on the VPC."""
        vpcs = self._get_vpcs(resources_by_type)
        main_vpc = [v for v in vpcs if v["values"].get("cidr_block") == "10.0.0.0/16"]
        assert len(main_vpc) == 1
        values = main_vpc[0]["values"]
        assert values.get("enable_dns_hostnames") is True, (
            "DNS hostnames must be enabled on the VPC"
        )

    def test_ac_001_5_vpc_tags(self, resources_by_type):
        """AC-001-5: VPC is tagged with Environment, Project, and Owner."""
        vpcs = self._get_vpcs(resources_by_type)
        main_vpc = [v for v in vpcs if v["values"].get("cidr_block") == "10.0.0.0/16"]
        assert len(main_vpc) == 1
        tags = main_vpc[0]["values"].get("tags", {}) or {}
        # Also check tags_all which includes provider default_tags
        tags_all = main_vpc[0]["values"].get("tags_all", {}) or {}
        combined = {**tags_all, **tags}
        for required_tag in ["Environment", "Project", "Owner"]:
            assert required_tag in combined, (
                f"VPC missing required tag '{required_tag}'. "
                f"Found tags: {list(combined.keys())}"
            )
