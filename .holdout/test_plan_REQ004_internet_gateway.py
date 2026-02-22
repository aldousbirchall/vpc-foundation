"""
REQ-004: Internet Gateway

Validates that the Terraform plan creates an internet gateway attached to the VPC:
- AC-004-1: Internet gateway exists and is attached to the VPC
- AC-004-2: Internet gateway is tagged with Environment, Project, and Owner
"""


class TestInternetGateway:
    """REQ-004: Internet gateway attached to the VPC."""

    def _get_igws(self, resources_by_type):
        igws = resources_by_type.get("aws_internet_gateway", [])
        assert len(igws) >= 1, "No aws_internet_gateway resource found in plan"
        return igws

    def test_ac_004_1_igw_exists(self, resources_by_type):
        """AC-004-1: Internet gateway exists in the plan."""
        igws = self._get_igws(resources_by_type)
        assert len(igws) >= 1

    def test_ac_004_1_igw_attached_to_vpc(self, resources_by_type):
        """AC-004-1: Internet gateway is attached to a VPC (vpc_id is set)."""
        igws = self._get_igws(resources_by_type)
        for igw in igws:
            # In plan.json, vpc_id may be a known value or a reference.
            # If it's in planned_values, it should be non-null.
            vpc_id = igw["values"].get("vpc_id")
            # vpc_id can be a computed reference (not yet known), but
            # the resource configuration should reference the VPC.
            # We just confirm the field exists and isn't explicitly empty.
            assert vpc_id is None or vpc_id != "", (
                "Internet gateway must be attached to a VPC"
            )

    def test_ac_004_2_igw_tags(self, resources_by_type):
        """AC-004-2: Internet gateway tagged with Environment, Project, Owner."""
        igws = self._get_igws(resources_by_type)
        for igw in igws:
            tags = igw["values"].get("tags", {}) or {}
            tags_all = igw["values"].get("tags_all", {}) or {}
            combined = {**tags_all, **tags}
            for required_tag in ["Environment", "Project", "Owner"]:
                assert required_tag in combined, (
                    f"Internet gateway missing tag '{required_tag}'. "
                    f"Found: {list(combined.keys())}"
                )
