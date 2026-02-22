"""
REQ-016: Terraform Plan Only

Validates that the build pipeline terminates at plan:
- AC-016-1: Makefile contains init, validate, plan targets
- AC-016-2: Makefile does not contain apply or destroy targets
"""
import re


class TestPlanOnly:
    """REQ-016: Build pipeline is plan-only. No apply or destroy."""

    def test_ac_016_1_makefile_has_init(self, makefile_content):
        """AC-016-1: Makefile contains an 'init' target."""
        assert re.search(r'^init\s*:', makefile_content, re.MULTILINE), (
            "Makefile does not have an 'init' target"
        )

    def test_ac_016_1_makefile_has_validate(self, makefile_content):
        """AC-016-1: Makefile contains a 'validate' target."""
        assert re.search(r'^validate\s*:', makefile_content, re.MULTILINE), (
            "Makefile does not have a 'validate' target"
        )

    def test_ac_016_1_makefile_has_plan(self, makefile_content):
        """AC-016-1: Makefile contains a 'plan' target."""
        assert re.search(r'^plan\s*:', makefile_content, re.MULTILINE), (
            "Makefile does not have a 'plan' target"
        )

    def test_ac_016_2_no_apply_target(self, makefile_content):
        """AC-016-2: Makefile does NOT contain an 'apply' target.

        This is a critical negative test. The foundation layer must not
        have an apply target to prevent accidental infrastructure provisioning.
        """
        apply_match = re.search(r'^apply\s*:', makefile_content, re.MULTILINE)
        assert apply_match is None, (
            "Makefile contains an 'apply' target. "
            "Foundation layer pipeline must terminate at 'plan'."
        )

    def test_ac_016_2_no_destroy_target(self, makefile_content):
        """AC-016-2: Makefile does NOT contain a 'destroy' target.

        Another critical negative test.
        """
        destroy_match = re.search(
            r'^destroy\s*:', makefile_content, re.MULTILINE
        )
        assert destroy_match is None, (
            "Makefile contains a 'destroy' target. "
            "Foundation layer pipeline must not have destroy capability."
        )

    def test_no_terraform_apply_command(self, makefile_content):
        """Negative: Makefile does not invoke 'terraform apply' anywhere."""
        assert "terraform apply" not in makefile_content, (
            "Makefile contains 'terraform apply' command. "
            "Pipeline must terminate at plan."
        )

    def test_no_terraform_destroy_command(self, makefile_content):
        """Negative: Makefile does not invoke 'terraform destroy' anywhere."""
        assert "terraform destroy" not in makefile_content, (
            "Makefile contains 'terraform destroy' command. "
            "Pipeline must not have destroy capability."
        )
