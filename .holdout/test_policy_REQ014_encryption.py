"""
REQ-014: Encryption

Validates encryption requirements:
- AC-014-1: Static assets S3 bucket has SSE-S3 (AES256) default encryption
- AC-014-2: Terraform state backend specifies encrypt = true
"""
import re


class TestEncryption:
    """REQ-014: Encryption on S3 buckets and state backend."""

    def test_ac_014_1_s3_encryption(self, resources_by_type):
        """AC-014-1: Static assets S3 bucket has AES256 encryption.

        This overlaps with REQ-009 AC-009-3. Tested again here as a
        policy check since it falls under the encryption requirement.
        """
        sse_resources = resources_by_type.get(
            "aws_s3_bucket_server_side_encryption_configuration", []
        )
        buckets = resources_by_type.get("aws_s3_bucket", [])

        encryption_found = False

        # Check separate SSE config resource
        for sse_r in sse_resources:
            rules = sse_r["values"].get("rule", [])
            if isinstance(rules, list):
                for rule in rules:
                    default = rule.get("apply_server_side_encryption_by_default", {})
                    if isinstance(default, list):
                        for d in default:
                            if d.get("sse_algorithm") in ("AES256", "aws:kms"):
                                encryption_found = True
                    elif isinstance(default, dict):
                        if default.get("sse_algorithm") in ("AES256", "aws:kms"):
                            encryption_found = True

        # Check inline on bucket
        if not encryption_found:
            for bucket in buckets:
                sse = bucket["values"].get("server_side_encryption_configuration", [])
                if isinstance(sse, list):
                    for config in sse:
                        rules = config.get("rule", [])
                        if isinstance(rules, list):
                            for rule in rules:
                                default = rule.get(
                                    "apply_server_side_encryption_by_default", {}
                                )
                                if isinstance(default, dict):
                                    if default.get("sse_algorithm") in ("AES256", "aws:kms"):
                                        encryption_found = True

        assert encryption_found, (
            "No S3 encryption configuration found with AES256 or aws:kms"
        )

    def test_ac_014_2_state_backend_encrypted(self, all_terraform_source):
        """AC-014-2: Terraform state backend has encrypt = true."""
        backend_match = re.search(
            r'backend\s+"s3"\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
            all_terraform_source,
            re.DOTALL,
        )
        assert backend_match, "No S3 backend block found"

        block = backend_match.group(1)
        assert re.search(r'encrypt\s*=\s*true', block), (
            "Backend S3 block does not specify 'encrypt = true'"
        )
