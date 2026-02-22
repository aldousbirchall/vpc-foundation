"""
REQ-003: Private Subnets

Validates that the Terraform plan creates two private subnets:
- AC-003-1: Private subnet in eu-west-1a with CIDR 10.0.10.0/24
- AC-003-2: Private subnet in eu-west-1b with CIDR 10.0.20.0/24
- AC-003-3: Neither subnet has map_public_ip_on_launch enabled
- AC-003-4: Both subnets are tagged with Environment, Project, and Owner
"""


class TestPrivateSubnets:
    """REQ-003: Two private subnets across eu-west-1a and eu-west-1b."""

    EXPECTED = {
        "eu-west-1a": "10.0.10.0/24",
        "eu-west-1b": "10.0.20.0/24",
    }

    def _get_private_subnets(self, resources_by_type):
        expected_cidrs = set(self.EXPECTED.values())
        subnets = resources_by_type.get("aws_subnet", [])
        return [
            s for s in subnets
            if s["values"].get("cidr_block") in expected_cidrs
        ]

    def test_ac_003_1_private_subnet_1a(self, resources_by_type):
        """AC-003-1: Private subnet in eu-west-1a with CIDR 10.0.10.0/24."""
        subnets = resources_by_type.get("aws_subnet", [])
        matching = [
            s for s in subnets
            if s["values"].get("cidr_block") == "10.0.10.0/24"
            and s["values"].get("availability_zone") == "eu-west-1a"
        ]
        assert len(matching) >= 1, (
            "No subnet found with CIDR 10.0.10.0/24 in eu-west-1a"
        )

    def test_ac_003_2_private_subnet_1b(self, resources_by_type):
        """AC-003-2: Private subnet in eu-west-1b with CIDR 10.0.20.0/24."""
        subnets = resources_by_type.get("aws_subnet", [])
        matching = [
            s for s in subnets
            if s["values"].get("cidr_block") == "10.0.20.0/24"
            and s["values"].get("availability_zone") == "eu-west-1b"
        ]
        assert len(matching) >= 1, (
            "No subnet found with CIDR 10.0.20.0/24 in eu-west-1b"
        )

    def test_ac_003_3_no_public_ip(self, resources_by_type):
        """AC-003-3: Neither private subnet has map_public_ip_on_launch enabled."""
        private_subnets = self._get_private_subnets(resources_by_type)
        assert len(private_subnets) == 2, (
            f"Expected 2 private subnets, found {len(private_subnets)}"
        )
        for subnet in private_subnets:
            cidr = subnet["values"]["cidr_block"]
            public_ip = subnet["values"].get("map_public_ip_on_launch", False)
            assert public_ip is not True, (
                f"Private subnet {cidr} must NOT have map_public_ip_on_launch enabled"
            )

    def test_ac_003_4_private_subnet_tags(self, resources_by_type):
        """AC-003-4: Both private subnets tagged with Environment, Project, Owner."""
        private_subnets = self._get_private_subnets(resources_by_type)
        assert len(private_subnets) == 2
        for subnet in private_subnets:
            cidr = subnet["values"]["cidr_block"]
            tags = subnet["values"].get("tags", {}) or {}
            tags_all = subnet["values"].get("tags_all", {}) or {}
            combined = {**tags_all, **tags}
            for required_tag in ["Environment", "Project", "Owner"]:
                assert required_tag in combined, (
                    f"Private subnet {cidr} missing tag '{required_tag}'. "
                    f"Found: {list(combined.keys())}"
                )
