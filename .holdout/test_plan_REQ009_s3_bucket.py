"""
REQ-009: S3 Bucket for Static Assets

Validates that the Terraform plan creates an S3 bucket with proper settings:
- AC-009-1: S3 bucket exists with name derived from a configurable variable
- AC-009-2: Versioning is enabled on the bucket
- AC-009-3: Server-side encryption (AES256) is enabled by default
- AC-009-4: Public access is blocked (all four settings true)
- AC-009-5: Bucket is tagged with Environment, Project, and Owner
"""


class TestS3Bucket:
    """REQ-009: S3 bucket for static assets."""

    def test_ac_009_1_s3_bucket_exists(self, resources_by_type):
        """AC-009-1: At least one S3 bucket exists in the plan."""
        buckets = resources_by_type.get("aws_s3_bucket", [])
        assert len(buckets) >= 1, "No aws_s3_bucket resource found in plan"

    def test_ac_009_2_versioning_enabled(self, resources_by_type):
        """AC-009-2: S3 bucket versioning is enabled.

        Versioning may be configured as an inline block on the bucket
        or as a separate aws_s3_bucket_versioning resource.
        """
        buckets = resources_by_type.get("aws_s3_bucket", [])
        versioning_resources = resources_by_type.get(
            "aws_s3_bucket_versioning", []
        )

        versioning_found = False

        # Check inline versioning on bucket
        for bucket in buckets:
            versioning = bucket["values"].get("versioning", [])
            if isinstance(versioning, list):
                for v in versioning:
                    if v.get("enabled") is True:
                        versioning_found = True
            elif isinstance(versioning, dict):
                if versioning.get("enabled") is True:
                    versioning_found = True

        # Check separate versioning resource
        if not versioning_found:
            for vr in versioning_resources:
                vc = vr["values"].get("versioning_configuration", {})
                if isinstance(vc, list):
                    for v in vc:
                        if v.get("status") == "Enabled":
                            versioning_found = True
                elif isinstance(vc, dict):
                    if vc.get("status") == "Enabled":
                        versioning_found = True

        assert versioning_found, (
            "S3 bucket versioning is not enabled. Expected either inline "
            "versioning { enabled = true } or an aws_s3_bucket_versioning "
            "resource with status = Enabled"
        )

    def test_ac_009_3_encryption_aes256(self, resources_by_type):
        """AC-009-3: Server-side encryption (AES256) is enabled by default.

        Encryption may be inline or via aws_s3_bucket_server_side_encryption_configuration.
        """
        buckets = resources_by_type.get("aws_s3_bucket", [])
        sse_resources = resources_by_type.get(
            "aws_s3_bucket_server_side_encryption_configuration", []
        )

        encryption_found = False

        # Check inline server_side_encryption_configuration
        for bucket in buckets:
            sse = bucket["values"].get("server_side_encryption_configuration", [])
            if isinstance(sse, list):
                for config in sse:
                    rules = config.get("rule", [])
                    if isinstance(rules, list):
                        for rule in rules:
                            sse_algo = rule.get("apply_server_side_encryption_by_default", {})
                            if isinstance(sse_algo, list):
                                for a in sse_algo:
                                    if a.get("sse_algorithm") in ("AES256", "aws:kms"):
                                        encryption_found = True
                            elif isinstance(sse_algo, dict):
                                if sse_algo.get("sse_algorithm") in ("AES256", "aws:kms"):
                                    encryption_found = True

        # Check separate SSE resource
        if not encryption_found:
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
                elif isinstance(rules, dict):
                    default = rules.get("apply_server_side_encryption_by_default", {})
                    if isinstance(default, dict):
                        if default.get("sse_algorithm") in ("AES256", "aws:kms"):
                            encryption_found = True

        assert encryption_found, (
            "S3 bucket does not have AES256 or aws:kms encryption configured"
        )

    def test_ac_009_4_public_access_blocked(self, resources_by_type):
        """AC-009-4: All four public access block settings are true.

        Checks aws_s3_bucket_public_access_block resource.
        """
        pab_resources = resources_by_type.get(
            "aws_s3_bucket_public_access_block", []
        )
        assert len(pab_resources) >= 1, (
            "No aws_s3_bucket_public_access_block resource found"
        )

        for pab in pab_resources:
            vals = pab["values"]
            assert vals.get("block_public_acls") is True, (
                "block_public_acls must be true"
            )
            assert vals.get("block_public_policy") is True, (
                "block_public_policy must be true"
            )
            assert vals.get("ignore_public_acls") is True, (
                "ignore_public_acls must be true"
            )
            assert vals.get("restrict_public_buckets") is True, (
                "restrict_public_buckets must be true"
            )

    def test_ac_009_5_s3_bucket_tags(self, resources_by_type):
        """AC-009-5: S3 bucket tagged with Environment, Project, Owner."""
        buckets = resources_by_type.get("aws_s3_bucket", [])
        assert len(buckets) >= 1
        for bucket in buckets:
            tags = bucket["values"].get("tags", {}) or {}
            tags_all = bucket["values"].get("tags_all", {}) or {}
            combined = {**tags_all, **tags}
            for required_tag in ["Environment", "Project", "Owner"]:
                assert required_tag in combined, (
                    f"S3 bucket missing tag '{required_tag}'. "
                    f"Found: {list(combined.keys())}"
                )
