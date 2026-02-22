"""
REQ-007: Web Tier Security Group

Validates that the Terraform plan creates a web tier security group:
- AC-007-1: Security group exists in the VPC
- AC-007-2: Ingress rule allows TCP port 80 from 0.0.0.0/0
- AC-007-3: Ingress rule allows TCP port 443 from 0.0.0.0/0
- AC-007-4: Egress rule allows all outbound traffic
- AC-007-5: Security group is tagged with Environment, Project, and Owner
"""


def _find_web_sg(resources_by_type):
    """Find security group(s) that have HTTP/HTTPS ingress rules.

    We identify the web SG by its ingress rules (port 80 and 443 from 0.0.0.0/0),
    not by its name, to remain implementation-agnostic.
    """
    sgs = resources_by_type.get("aws_security_group", [])
    candidates = []

    for sg in sgs:
        ingress = sg["values"].get("ingress", []) or []
        has_80 = any(
            _rule_matches_port(r, 80) and _rule_has_cidr(r, "0.0.0.0/0")
            for r in ingress
        )
        has_443 = any(
            _rule_matches_port(r, 443) and _rule_has_cidr(r, "0.0.0.0/0")
            for r in ingress
        )
        if has_80 or has_443:
            candidates.append(sg)

    return candidates


def _find_web_sg_rules(resources_by_type):
    """Find standalone security group rules for web tier (port 80/443).

    Some implementations use aws_security_group_rule or
    aws_vpc_security_group_ingress_rule instead of inline rules.
    """
    rule_types = [
        "aws_security_group_rule",
        "aws_vpc_security_group_ingress_rule",
    ]
    rules = []
    for rt in rule_types:
        rules.extend(resources_by_type.get(rt, []))
    return rules


def _rule_matches_port(rule, port):
    """Check if an inline ingress rule matches a specific port."""
    from_port = rule.get("from_port", -1)
    to_port = rule.get("to_port", -1)
    return from_port <= port <= to_port


def _rule_has_cidr(rule, cidr):
    """Check if an inline rule includes the given CIDR."""
    cidr_blocks = rule.get("cidr_blocks", []) or []
    return cidr in cidr_blocks


class TestWebSecurityGroup:
    """REQ-007: Web tier security group with HTTP/HTTPS ingress."""

    def test_ac_007_1_web_sg_exists(self, resources_by_type):
        """AC-007-1: At least one security group exists in the plan."""
        sgs = resources_by_type.get("aws_security_group", [])
        assert len(sgs) >= 1, "No aws_security_group resources found in plan"

    def test_ac_007_2_port_80_ingress(self, resources_by_type):
        """AC-007-2: Ingress rule allows TCP port 80 from 0.0.0.0/0."""
        # Check inline rules on SGs
        web_sgs = _find_web_sg(resources_by_type)
        standalone_rules = _find_web_sg_rules(resources_by_type)

        port_80_found = False

        # Check inline ingress
        for sg in web_sgs:
            ingress = sg["values"].get("ingress", []) or []
            for r in ingress:
                if _rule_matches_port(r, 80) and _rule_has_cidr(r, "0.0.0.0/0"):
                    protocol = r.get("protocol", "").lower()
                    if protocol in ("tcp", "6", "-1"):
                        port_80_found = True

        # Check standalone rules
        if not port_80_found:
            for rule in standalone_rules:
                vals = rule["values"]
                from_port = vals.get("from_port", -1)
                to_port = vals.get("to_port", -1)
                cidr = vals.get("cidr_ipv4", "") or ""
                cidr_blocks = vals.get("cidr_blocks", []) or []
                protocol = (vals.get("ip_protocol", "") or vals.get("protocol", "")).lower()
                rule_type = vals.get("type", "ingress")

                port_match = (from_port is not None and to_port is not None
                              and from_port <= 80 <= to_port)
                cidr_match = cidr == "0.0.0.0/0" or "0.0.0.0/0" in cidr_blocks
                proto_match = protocol in ("tcp", "6", "-1")
                is_ingress = rule_type == "ingress" or rule["type"].endswith("ingress_rule")

                if port_match and cidr_match and proto_match and is_ingress:
                    port_80_found = True

        assert port_80_found, (
            "No ingress rule found allowing TCP port 80 from 0.0.0.0/0"
        )

    def test_ac_007_3_port_443_ingress(self, resources_by_type):
        """AC-007-3: Ingress rule allows TCP port 443 from 0.0.0.0/0."""
        web_sgs = _find_web_sg(resources_by_type)
        standalone_rules = _find_web_sg_rules(resources_by_type)

        port_443_found = False

        for sg in web_sgs:
            ingress = sg["values"].get("ingress", []) or []
            for r in ingress:
                if _rule_matches_port(r, 443) and _rule_has_cidr(r, "0.0.0.0/0"):
                    protocol = r.get("protocol", "").lower()
                    if protocol in ("tcp", "6", "-1"):
                        port_443_found = True

        if not port_443_found:
            for rule in standalone_rules:
                vals = rule["values"]
                from_port = vals.get("from_port", -1)
                to_port = vals.get("to_port", -1)
                cidr = vals.get("cidr_ipv4", "") or ""
                cidr_blocks = vals.get("cidr_blocks", []) or []
                protocol = (vals.get("ip_protocol", "") or vals.get("protocol", "")).lower()
                rule_type = vals.get("type", "ingress")

                port_match = (from_port is not None and to_port is not None
                              and from_port <= 443 <= to_port)
                cidr_match = cidr == "0.0.0.0/0" or "0.0.0.0/0" in cidr_blocks
                proto_match = protocol in ("tcp", "6", "-1")
                is_ingress = rule_type == "ingress" or rule["type"].endswith("ingress_rule")

                if port_match and cidr_match and proto_match and is_ingress:
                    port_443_found = True

        assert port_443_found, (
            "No ingress rule found allowing TCP port 443 from 0.0.0.0/0"
        )

    def test_ac_007_4_egress_all(self, resources_by_type):
        """AC-007-4: Egress rule allows all outbound traffic."""
        web_sgs = _find_web_sg(resources_by_type)
        standalone_rules = _find_web_sg_rules(resources_by_type)

        egress_all_found = False

        # Check inline egress
        for sg in web_sgs:
            egress = sg["values"].get("egress", []) or []
            for r in egress:
                cidr_blocks = r.get("cidr_blocks", []) or []
                protocol = r.get("protocol", "").lower()
                if "0.0.0.0/0" in cidr_blocks and protocol == "-1":
                    egress_all_found = True

        # Check standalone egress rules
        if not egress_all_found:
            egress_rule_types = [
                "aws_security_group_rule",
                "aws_vpc_security_group_egress_rule",
            ]
            for rt in egress_rule_types:
                for rule in resources_by_type.get(rt, []):
                    vals = rule["values"]
                    cidr = vals.get("cidr_ipv4", "") or ""
                    cidr_blocks = vals.get("cidr_blocks", []) or []
                    protocol = (vals.get("ip_protocol", "") or vals.get("protocol", "")).lower()
                    rule_type = vals.get("type", "")
                    is_egress = rule_type == "egress" or rule["type"].endswith("egress_rule")

                    cidr_match = cidr == "0.0.0.0/0" or "0.0.0.0/0" in cidr_blocks
                    if cidr_match and protocol == "-1" and is_egress:
                        egress_all_found = True

        assert egress_all_found, (
            "No egress rule found allowing all outbound traffic (protocol -1, 0.0.0.0/0)"
        )

    def test_ac_007_5_web_sg_tags(self, resources_by_type):
        """AC-007-5: Web security group tagged with Environment, Project, Owner."""
        sgs = resources_by_type.get("aws_security_group", [])
        assert len(sgs) >= 1

        # Check that at least one SG has required tags (the web SG)
        any_sg_tagged = False
        for sg in sgs:
            tags = sg["values"].get("tags", {}) or {}
            tags_all = sg["values"].get("tags_all", {}) or {}
            combined = {**tags_all, **tags}
            if all(t in combined for t in ["Environment", "Project", "Owner"]):
                any_sg_tagged = True

        assert any_sg_tagged, (
            "No security group has all required tags (Environment, Project, Owner)"
        )
