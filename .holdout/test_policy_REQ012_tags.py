"""
REQ-012: Required Tagging

Validates tagging policy:
- AC-012-1: Provider default_tags block includes Environment, Project, Owner, ManagedBy
- AC-012-2: All resources in the plan carry these tags
"""
import re


REQUIRED_TAGS = {"Environment", "Project", "Owner", "ManagedBy"}

# Resource types that support tags in AWS
TAGGABLE_TYPES = {
    "aws_vpc",
    "aws_subnet",
    "aws_internet_gateway",
    "aws_nat_gateway",
    "aws_eip",
    "aws_route_table",
    "aws_security_group",
    "aws_s3_bucket",
}


class TestRequiredTags:
    """REQ-012: Required tagging on all resources."""

    def test_ac_012_1_default_tags_in_provider(self, all_terraform_source):
        """AC-012-1: Provider block includes default_tags with required tags.

        Checks the .tf source for a default_tags block containing
        Environment, Project, Owner, and ManagedBy.
        """
        # Find default_tags block
        has_default_tags = re.search(
            r'default_tags\s*\{', all_terraform_source
        )
        assert has_default_tags, (
            "No default_tags block found in provider configuration"
        )

        # Extract the default_tags block content
        # Look for the tags sub-block within default_tags
        dt_match = re.search(
            r'default_tags\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
            all_terraform_source,
            re.DOTALL,
        )
        if dt_match:
            dt_block = dt_match.group(1)
            for tag in REQUIRED_TAGS:
                assert re.search(rf'{tag}\s*=', dt_block, re.IGNORECASE), (
                    f"default_tags block missing '{tag}' tag"
                )

    def test_ac_012_2_all_taggable_resources_tagged(self, resources_by_type):
        """AC-012-2: All taggable resources carry required tags.

        Checks tags or tags_all on every resource of a taggable type.
        Provider default_tags propagate into tags_all in the plan.
        """
        missing = []
        for rtype in TAGGABLE_TYPES:
            for resource in resources_by_type.get(rtype, []):
                tags = resource["values"].get("tags", {}) or {}
                tags_all = resource["values"].get("tags_all", {}) or {}
                combined = {**tags_all, **tags}
                for tag in REQUIRED_TAGS:
                    if tag not in combined:
                        addr = resource.get("address", f"{rtype}.unknown")
                        missing.append(f"{addr} missing '{tag}'")

        assert not missing, (
            f"Resources with missing required tags:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )

    def test_ac_012_2_tag_values_not_empty(self, resources_by_type):
        """AC-012-2: Tag values are not empty strings."""
        empty_tags = []
        for rtype in TAGGABLE_TYPES:
            for resource in resources_by_type.get(rtype, []):
                tags = resource["values"].get("tags", {}) or {}
                tags_all = resource["values"].get("tags_all", {}) or {}
                combined = {**tags_all, **tags}
                for tag in REQUIRED_TAGS:
                    if tag in combined and not combined[tag]:
                        addr = resource.get("address", f"{rtype}.unknown")
                        empty_tags.append(f"{addr}.{tag} is empty")

        assert not empty_tags, (
            f"Resources with empty tag values:\n"
            + "\n".join(f"  - {e}" for e in empty_tags)
        )
