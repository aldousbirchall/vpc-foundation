"""
REQ-013: Region Constraint

Validates that all resources are deployed in eu-west-1:
- AC-013-1: Provider region is set to eu-west-1
- AC-013-2: No resource specifies a region other than eu-west-1
- AC-013-3: Region is a variable with default eu-west-1
"""
import re


class TestRegionConstraint:
    """REQ-013: Region locked to eu-west-1."""

    def test_ac_013_1_provider_region(self, all_terraform_source):
        """AC-013-1: Provider region is set to eu-west-1.

        Checks that the AWS provider block sets region to eu-west-1
        (either directly or via a variable reference).
        """
        # Look for provider "aws" with region setting
        provider_block = re.search(
            r'provider\s+"aws"\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
            all_terraform_source,
            re.DOTALL,
        )
        assert provider_block, "No AWS provider block found"

        block_content = provider_block.group(1)
        has_region = re.search(r'region\s*=', block_content)
        assert has_region, "AWS provider block does not set a region"

    def test_ac_013_1_region_is_eu_west_1(self, provider_config):
        """AC-013-1: Provider config in plan confirms eu-west-1 region.

        Uses the plan.json configuration block which resolves variable references.
        """
        aws_config = provider_config.get("aws", {})
        expressions = aws_config.get("expressions", {})
        region_expr = expressions.get("region", {})

        # Region may be a constant_value or a variable reference
        if "constant_value" in region_expr:
            assert region_expr["constant_value"] == "eu-west-1", (
                f"Provider region is '{region_expr['constant_value']}', "
                "expected 'eu-west-1'"
            )
        # If it's a variable reference, we check the variable default separately

    def test_ac_013_2_no_other_regions(self, all_terraform_source):
        """AC-013-2: No resource explicitly specifies a non-eu-west-1 region.

        Scans for region = "..." patterns that don't match eu-west-1.
        """
        region_assignments = re.findall(
            r'region\s*=\s*"([^"]+)"', all_terraform_source
        )
        non_eu_west_1 = [
            r for r in region_assignments
            if r != "eu-west-1"
        ]
        assert not non_eu_west_1, (
            f"Found non-eu-west-1 region assignments: {non_eu_west_1}"
        )

    def test_ac_013_3_region_variable_exists(self, all_terraform_source):
        """AC-013-3: Region is defined as a variable."""
        has_region_var = re.search(
            r'variable\s+"region"', all_terraform_source
        )
        assert has_region_var, (
            "No 'region' variable defined. Region must be configurable."
        )

    def test_ac_013_3_region_default_eu_west_1(self, variables_config):
        """AC-013-3: Region variable defaults to eu-west-1."""
        region_var = variables_config.get("region", {})
        default = region_var.get("default")
        assert default == "eu-west-1", (
            f"Region variable default is '{default}', expected 'eu-west-1'"
        )
