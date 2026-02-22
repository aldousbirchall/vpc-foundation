"""
REQ-002: Public Subnets

Validates that the Terraform plan creates two public subnets with correct properties:
- AC-002-1: Public subnet in eu-west-1a with CIDR 10.0.1.0/24
- AC-002-2: Public subnet in eu-west-1b with CIDR 10.0.2.0/24
- AC-002-3: Both subnets have map_public_ip_on_launch enabled
- AC-002-4: Both subnets are tagged with Environment, Project, and Owner
"""


class TestPublicSubnets:
    """REQ-002: Two public subnets across eu-west-1a and eu-west-1b."""

    EXPECTED = {
        "eu-west-1a": "10.0.1.0/24",
        "eu-west-1b": "10.0.2.0/24",
    }

    def _get_public_subnets(self, resources_by_type):
        """Return subnets that match the expected public CIDRs."""
        subnets = resources_by_type.get("aws_subnet", [])
        expected_cidrs = set(self.EXPECTED.values())
        return [
            s for s in subnets
            if s["values"].get("cidr_block") in expected_cidrs
        ]

    def test_ac_002_1_public_subnet_1a(self, resources_by_type):
        """AC-002-1: Public subnet in eu-west-1a with CIDR 10.0.1.0/24."""
        subnets = resources_by_type.get("aws_subnet", [])
        matching = [
            s for s in subnets
            if s["values"].get("cidr_block") == "10.0.1.0/24"
            and s["values"].get("availability_zone") == "eu-west-1a"
        ]
        assert len(matching) >= 1, (
            "No subnet found with CIDR 10.0.1.0/24 in eu-west-1a"
        )

    def test_ac_002_2_public_subnet_1b(self, resources_by_type):
        """AC-002-2: Public subnet in eu-west-1b with CIDR 10.0.2.0/24."""
        subnets = resources_by_type.get("aws_subnet", [])
        matching = [
            s for s in subnets
            if s["values"].get("cidr_block") == "10.0.2.0/24"
            and s["values"].get("availability_zone") == "eu-west-1b"
        ]
        assert len(matching) >= 1, (
            "No subnet found with CIDR 10.0.2.0/24 in eu-west-1b"
        )

    def test_ac_002_3_public_ip_on_launch(self, resources_by_type):
        """AC-002-3: Both public subnets have map_public_ip_on_launch enabled."""
        public_subnets = self._get_public_subnets(resources_by_type)
        assert len(public_subnets) == 2, (
            f"Expected 2 public subnets, found {len(public_subnets)}"
        )
        for subnet in public_subnets:
            cidr = subnet["values"]["cidr_block"]
            assert subnet["values"].get("map_public_ip_on_launch") is True, (
                f"Public subnet {cidr} must have map_public_ip_on_launch = true"
            )

    def test_ac_002_4_public_subnet_tags(self, resources_by_type):
        """AC-002-4: Both public subnets tagged with Environment, Project, Owner."""
        public_subnets = self._get_public_subnets(resources_by_type)
        assert len(public_subnets) == 2
        for subnet in public_subnets:
            cidr = subnet["values"]["cidr_block"]
            tags = subnet["values"].get("tags", {}) or {}
            tags_all = subnet["values"].get("tags_all", {}) or {}
            combined = {**tags_all, **tags}
            for required_tag in ["Environment", "Project", "Owner"]:
                assert required_tag in combined, (
                    f"Public subnet {cidr} missing tag '{required_tag}'. "
                    f"Found: {list(combined.keys())}"
                )
