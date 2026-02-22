"""
REQ-015: No Hardcoded Environment Values

Validates that all environment-specific values are configurable via variables:
- AC-015-1: Every environment-specific value is a Terraform variable
- AC-015-2: Every variable has a description attribute
- AC-015-3: Defaults provided for region (eu-west-1), AZs, and CIDR blocks
"""
import re


class TestVariableConfiguration:
    """REQ-015: Variables for all environment-specific values."""

    def _extract_variable_blocks(self, all_terraform_source):
        """Extract all variable blocks as (name, block_content) tuples."""
        pattern = r'variable\s+"([^"]+)"\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        return re.findall(pattern, all_terraform_source, re.DOTALL)

    def test_ac_015_1_region_is_variable(self, all_terraform_source):
        """AC-015-1: Region is a Terraform variable."""
        assert re.search(r'variable\s+"region"', all_terraform_source), (
            "Region must be defined as a variable"
        )

    def test_ac_015_1_azs_are_variable(self, all_terraform_source):
        """AC-015-1: Availability zones are configurable via variable(s)."""
        has_az_var = re.search(
            r'variable\s+"[^"]*(?:az|availability_zone)[^"]*"',
            all_terraform_source,
            re.IGNORECASE,
        )
        assert has_az_var, (
            "No variable found for availability zones. "
            "AZs must be configurable, not hardcoded."
        )

    def test_ac_015_1_cidr_is_variable(self, all_terraform_source):
        """AC-015-1: VPC CIDR block is configurable via a variable."""
        has_cidr_var = re.search(
            r'variable\s+"[^"]*cidr[^"]*"',
            all_terraform_source,
            re.IGNORECASE,
        )
        assert has_cidr_var, (
            "No variable found for CIDR blocks. "
            "CIDR blocks must be configurable, not hardcoded."
        )

    def test_ac_015_1_bucket_name_is_variable(self, all_terraform_source):
        """AC-015-1: S3 bucket name is derived from a configurable variable."""
        has_bucket_var = re.search(
            r'variable\s+"[^"]*bucket[^"]*"',
            all_terraform_source,
            re.IGNORECASE,
        )
        # Also accept project_name or similar that could be used to derive bucket name
        has_project_var = re.search(
            r'variable\s+"[^"]*(?:project|name)[^"]*"',
            all_terraform_source,
            re.IGNORECASE,
        )
        assert has_bucket_var or has_project_var, (
            "No variable found for S3 bucket name or project name. "
            "Bucket name must be configurable."
        )

    def test_ac_015_2_all_variables_have_descriptions(self, all_terraform_source):
        """AC-015-2: Every variable has a description attribute."""
        variable_blocks = self._extract_variable_blocks(all_terraform_source)
        assert len(variable_blocks) > 0, "No variables found in Terraform source"

        missing_descriptions = []
        for name, block_content in variable_blocks:
            if not re.search(r'description\s*=', block_content):
                missing_descriptions.append(name)

        assert not missing_descriptions, (
            f"Variables without descriptions: {missing_descriptions}"
        )

    def test_ac_015_3_region_default(self, variables_config):
        """AC-015-3: Region variable has default eu-west-1."""
        region = variables_config.get("region", {})
        assert region.get("default") == "eu-west-1", (
            f"Region variable default is '{region.get('default')}', "
            "expected 'eu-west-1'"
        )

    def test_ac_015_3_az_defaults_provided(self, all_terraform_source):
        """AC-015-3: AZ variable has defaults provided."""
        # Find the AZ variable block and check for a default
        az_blocks = re.findall(
            r'variable\s+"([^"]*(?:az|availability_zone)[^"]*)"\s*\{'
            r'([^}]*(?:\{[^}]*\}[^}]*)*)\}',
            all_terraform_source,
            re.DOTALL | re.IGNORECASE,
        )
        assert len(az_blocks) > 0, "No AZ variable found"

        has_default = False
        for name, block in az_blocks:
            if re.search(r'default\s*=', block):
                has_default = True

        assert has_default, (
            "AZ variable(s) do not have defaults. "
            "Defaults must be provided for AZs."
        )

    def test_ac_015_3_cidr_defaults_provided(self, all_terraform_source):
        """AC-015-3: CIDR variable has defaults provided."""
        cidr_blocks = re.findall(
            r'variable\s+"([^"]*cidr[^"]*)"\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
            all_terraform_source,
            re.DOTALL | re.IGNORECASE,
        )
        assert len(cidr_blocks) > 0, "No CIDR variable found"

        has_default = False
        for name, block in cidr_blocks:
            if re.search(r'default\s*=', block):
                has_default = True

        assert has_default, (
            "CIDR variable(s) do not have defaults. "
            "Defaults must be provided for CIDR blocks."
        )

    def test_minimum_variable_count(self, all_terraform_source):
        """Structural: At least 5 variables expected (region, AZs, CIDRs, env, project)."""
        variable_blocks = self._extract_variable_blocks(all_terraform_source)
        assert len(variable_blocks) >= 5, (
            f"Expected at least 5 variables, found {len(variable_blocks)}. "
            "Region, AZs, CIDRs, environment, and project name should all be variables."
        )
