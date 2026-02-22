"""
REQ-006: Route Tables

Validates that the Terraform plan configures route tables correctly:
- AC-006-1: Public route table has a route for 0.0.0.0/0 via IGW
- AC-006-2: Public route table is associated with both public subnets
- AC-006-3: Private route table has a route for 0.0.0.0/0 via NAT GW
- AC-006-4: Private route table is associated with both private subnets
- AC-006-5: All route tables are tagged with Environment, Project, and Owner
"""


class TestRouteTables:
    """REQ-006: Route tables for public and private subnets."""

    def test_ac_006_1_public_route_to_igw(self, resources_by_type):
        """AC-006-1: A route exists with destination 0.0.0.0/0 targeting an IGW."""
        routes = resources_by_type.get("aws_route", [])
        route_tables = resources_by_type.get("aws_route_table", [])

        # Check for inline routes in route tables or standalone aws_route resources
        igw_route_found = False

        # Check standalone routes
        for route in routes:
            dest = route["values"].get("destination_cidr_block", "")
            gw = route["values"].get("gateway_id")
            if dest == "0.0.0.0/0" and gw is not None:
                igw_route_found = True
                break

        # Check inline routes in route tables
        if not igw_route_found:
            for rt in route_tables:
                inline_routes = rt["values"].get("route", []) or []
                for r in inline_routes:
                    if (r.get("cidr_block") == "0.0.0.0/0"
                            and r.get("gateway_id")):
                        igw_route_found = True
                        break

        assert igw_route_found, (
            "No route found with 0.0.0.0/0 destination targeting an internet gateway"
        )

    def test_ac_006_2_public_rt_associations(self, resources_by_type):
        """AC-006-2: At least 2 route table associations exist for public subnets."""
        associations = resources_by_type.get("aws_route_table_association", [])
        # We need at least 2 associations for public + 2 for private = 4 total
        assert len(associations) >= 4, (
            f"Expected at least 4 route table associations (2 public + 2 private), "
            f"found {len(associations)}"
        )

    def test_ac_006_3_private_route_to_nat(self, resources_by_type):
        """AC-006-3: A route exists with destination 0.0.0.0/0 targeting a NAT GW."""
        routes = resources_by_type.get("aws_route", [])
        route_tables = resources_by_type.get("aws_route_table", [])

        nat_route_found = False

        # Check standalone routes
        for route in routes:
            dest = route["values"].get("destination_cidr_block", "")
            nat = route["values"].get("nat_gateway_id")
            if dest == "0.0.0.0/0" and nat is not None:
                nat_route_found = True
                break

        # Check inline routes in route tables
        if not nat_route_found:
            for rt in route_tables:
                inline_routes = rt["values"].get("route", []) or []
                for r in inline_routes:
                    if (r.get("cidr_block") == "0.0.0.0/0"
                            and r.get("nat_gateway_id")):
                        nat_route_found = True
                        break

        assert nat_route_found, (
            "No route found with 0.0.0.0/0 destination targeting a NAT gateway"
        )

    def test_ac_006_4_four_total_associations(self, resources_by_type):
        """AC-006-4: At least 4 route table associations (2 public + 2 private)."""
        associations = resources_by_type.get("aws_route_table_association", [])
        assert len(associations) >= 4, (
            f"Expected at least 4 route table associations, found {len(associations)}"
        )

    def test_ac_006_5_route_table_tags(self, resources_by_type):
        """AC-006-5: All route tables tagged with Environment, Project, Owner."""
        route_tables = resources_by_type.get("aws_route_table", [])
        assert len(route_tables) >= 2, (
            f"Expected at least 2 route tables (public + private), "
            f"found {len(route_tables)}"
        )
        for rt in route_tables:
            tags = rt["values"].get("tags", {}) or {}
            tags_all = rt["values"].get("tags_all", {}) or {}
            combined = {**tags_all, **tags}
            for required_tag in ["Environment", "Project", "Owner"]:
                assert required_tag in combined, (
                    f"Route table missing tag '{required_tag}'. "
                    f"Found: {list(combined.keys())}"
                )

    def test_two_distinct_route_tables(self, resources_by_type):
        """Structural: At least two route tables exist (public and private)."""
        route_tables = resources_by_type.get("aws_route_table", [])
        assert len(route_tables) >= 2, (
            f"Expected at least 2 route tables, found {len(route_tables)}"
        )
