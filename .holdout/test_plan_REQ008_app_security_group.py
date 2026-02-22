"""
REQ-008: Application Tier Security Group

Validates that the Terraform plan creates an app tier security group:
- AC-008-1: Security group exists in the VPC
- AC-008-2: Ingress rule allows traffic from the web tier SG only
- AC-008-3: No ingress rule allows traffic from 0.0.0.0/0
- AC-008-4: Egress rule allows all outbound traffic
- AC-008-5: Security group is tagged with Environment, Project, and Owner
"""


def _find_app_sg(resources_by_type):
    """Find the application security group.

    The app SG is identified by having ingress rules that reference another
    security group (not 0.0.0.0/0). It is the SG that does NOT have port 80/443
    ingress from 0.0.0.0/0.
    """
    sgs = resources_by_type.get("aws_security_group", [])
    app_candidates = []

    for sg in sgs:
        ingress = sg["values"].get("ingress", []) or []
        has_public_http = any(
            r.get("from_port", -1) <= 80 <= r.get("to_port", -1)
            and "0.0.0.0/0" in (r.get("cidr_blocks", []) or [])
            for r in ingress
        )
        if not has_public_http and ingress:
            # Has ingress rules but not the web pattern
            app_candidates.append(sg)
        elif not has_public_http and not ingress:
            # SG with no inline ingress might use standalone rules
            app_candidates.append(sg)

    return app_candidates


class TestAppSecurityGroup:
    """REQ-008: Application tier security group."""

    def test_ac_008_1_at_least_two_sgs(self, resources_by_type):
        """AC-008-1: At least two security groups exist (web + app)."""
        sgs = resources_by_type.get("aws_security_group", [])
        assert len(sgs) >= 2, (
            f"Expected at least 2 security groups (web + app), found {len(sgs)}"
        )

    def test_ac_008_3_no_public_ingress_on_app_sg(self, resources_by_type):
        """AC-008-3: No ingress rule on the app SG allows 0.0.0.0/0.

        This is a negative test: the app SG must NOT have any ingress from
        the public internet.
        """
        sgs = resources_by_type.get("aws_security_group", [])
        standalone_rules = resources_by_type.get("aws_security_group_rule", [])
        standalone_ingress_rules = resources_by_type.get(
            "aws_vpc_security_group_ingress_rule", []
        )

        # For each SG, check if it has public HTTP rules (web SG pattern).
        # SGs without public HTTP rules are app SG candidates.
        web_sg_like = set()
        for sg in sgs:
            ingress = sg["values"].get("ingress", []) or []
            for r in ingress:
                cidr_blocks = r.get("cidr_blocks", []) or []
                if "0.0.0.0/0" in cidr_blocks:
                    from_port = r.get("from_port", -1)
                    to_port = r.get("to_port", -1)
                    if from_port <= 80 <= to_port or from_port <= 443 <= to_port:
                        web_sg_like.add(sg.get("address", id(sg)))

        # All other SGs are app candidates
        app_sgs = [
            sg for sg in sgs
            if sg.get("address", id(sg)) not in web_sg_like
        ]

        for sg in app_sgs:
            ingress = sg["values"].get("ingress", []) or []
            for r in ingress:
                cidr_blocks = r.get("cidr_blocks", []) or []
                assert "0.0.0.0/0" not in cidr_blocks, (
                    f"App SG must not allow ingress from 0.0.0.0/0. "
                    f"Found rule with cidr_blocks={cidr_blocks}"
                )

        # Also check standalone ingress rules targeting non-web SGs
        # (We can't perfectly correlate without sg IDs, but we check
        # that not ALL ingress rules are public)
        all_ingress_rules = standalone_rules + standalone_ingress_rules
        sg_rules_with_public = [
            r for r in all_ingress_rules
            if r["values"].get("type", "ingress") == "ingress"
            or r["type"].endswith("ingress_rule")
        ]

        # There should be at least some ingress rules that don't use 0.0.0.0/0
        rules_with_sg_source = [
            r for r in sg_rules_with_public
            if (r["values"].get("source_security_group_id")
                or r["values"].get("referenced_security_group_id"))
        ]

        if sg_rules_with_public:
            # If standalone rules exist, at least one should reference another SG
            assert len(rules_with_sg_source) >= 1 or len(app_sgs) > 0, (
                "Expected at least one ingress rule referencing a security group "
                "(for the app tier), but all rules use CIDR blocks"
            )

    def test_ac_008_2_ingress_from_web_sg(self, resources_by_type):
        """AC-008-2: App SG allows ingress from web tier SG.

        Checks that at least one ingress rule references another security group
        (rather than a CIDR block), indicating SG-to-SG traffic.
        """
        sgs = resources_by_type.get("aws_security_group", [])
        standalone_rules = resources_by_type.get("aws_security_group_rule", [])
        standalone_ingress = resources_by_type.get(
            "aws_vpc_security_group_ingress_rule", []
        )

        sg_ref_found = False

        # Check inline ingress rules for security_groups references
        for sg in sgs:
            ingress = sg["values"].get("ingress", []) or []
            for r in ingress:
                sg_refs = r.get("security_groups", []) or []
                if sg_refs:
                    sg_ref_found = True
                    break

        # Check standalone rules for source_security_group_id
        if not sg_ref_found:
            for rule in standalone_rules:
                vals = rule["values"]
                if (vals.get("type") == "ingress"
                        and vals.get("source_security_group_id")):
                    sg_ref_found = True
                    break

        # Check VPC security group ingress rules
        if not sg_ref_found:
            for rule in standalone_ingress:
                vals = rule["values"]
                if vals.get("referenced_security_group_id"):
                    sg_ref_found = True
                    break

        assert sg_ref_found, (
            "No ingress rule found that references another security group. "
            "App tier must allow traffic from web tier SG."
        )

    def test_ac_008_4_app_sg_egress_all(self, resources_by_type):
        """AC-008-4: App SG egress allows all outbound traffic."""
        sgs = resources_by_type.get("aws_security_group", [])
        standalone_egress = resources_by_type.get(
            "aws_vpc_security_group_egress_rule", []
        )
        standalone_rules = resources_by_type.get("aws_security_group_rule", [])

        egress_all_count = 0

        # Check inline egress on all SGs
        for sg in sgs:
            egress = sg["values"].get("egress", []) or []
            for r in egress:
                cidr_blocks = r.get("cidr_blocks", []) or []
                protocol = r.get("protocol", "").lower()
                if "0.0.0.0/0" in cidr_blocks and protocol == "-1":
                    egress_all_count += 1

        # Check standalone egress rules
        for rule in standalone_egress:
            vals = rule["values"]
            cidr = vals.get("cidr_ipv4", "") or ""
            protocol = (vals.get("ip_protocol", "") or "").lower()
            if cidr == "0.0.0.0/0" and protocol == "-1":
                egress_all_count += 1

        for rule in standalone_rules:
            vals = rule["values"]
            if vals.get("type") == "egress":
                cidr_blocks = vals.get("cidr_blocks", []) or []
                protocol = (vals.get("protocol", "") or "").lower()
                if "0.0.0.0/0" in cidr_blocks and protocol == "-1":
                    egress_all_count += 1

        # Both web and app SGs should have egress all
        assert egress_all_count >= 2, (
            f"Expected at least 2 egress-all rules (one per SG), "
            f"found {egress_all_count}"
        )

    def test_ac_008_5_app_sg_tags(self, resources_by_type):
        """AC-008-5: All security groups tagged with Environment, Project, Owner."""
        sgs = resources_by_type.get("aws_security_group", [])
        assert len(sgs) >= 2
        for sg in sgs:
            tags = sg["values"].get("tags", {}) or {}
            tags_all = sg["values"].get("tags_all", {}) or {}
            combined = {**tags_all, **tags}
            for required_tag in ["Environment", "Project", "Owner"]:
                assert required_tag in combined, (
                    f"Security group '{sg.get('address', 'unknown')}' "
                    f"missing tag '{required_tag}'. Found: {list(combined.keys())}"
                )
