"""
REQ-010: Remote State Backend

Static analysis of Terraform source to validate remote state configuration:
- AC-010-1: Backend is configured as S3 with bucket, key, and region
- AC-010-2: DynamoDB table is specified for state locking
- AC-010-3: Backend encryption is enabled
- AC-010-4: Backend bucket has versioning enabled (checked in config)
"""
import re


class TestRemoteStateBackend:
    """REQ-010: Remote state backend configuration (static analysis)."""

    def _find_backend_block(self, all_terraform_source):
        """Extract the backend "s3" block from the Terraform source."""
        # Match: backend "s3" { ... }
        pattern = r'backend\s+"s3"\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        match = re.search(pattern, all_terraform_source, re.DOTALL)
        return match.group(1) if match else None

    def test_ac_010_1_backend_is_s3(self, all_terraform_source):
        """AC-010-1: Backend is configured as S3."""
        assert re.search(r'backend\s+"s3"', all_terraform_source), (
            "No S3 backend configuration found in Terraform source"
        )

    def test_ac_010_1_backend_has_bucket(self, all_terraform_source):
        """AC-010-1: Backend specifies a bucket."""
        block = self._find_backend_block(all_terraform_source)
        assert block is not None, "No backend s3 block found"
        assert re.search(r'bucket\s*=', block), (
            "Backend S3 block does not specify a 'bucket'"
        )

    def test_ac_010_1_backend_has_key(self, all_terraform_source):
        """AC-010-1: Backend specifies a key."""
        block = self._find_backend_block(all_terraform_source)
        assert block is not None, "No backend s3 block found"
        assert re.search(r'key\s*=', block), (
            "Backend S3 block does not specify a 'key'"
        )

    def test_ac_010_1_backend_has_region(self, all_terraform_source):
        """AC-010-1: Backend specifies a region."""
        block = self._find_backend_block(all_terraform_source)
        assert block is not None, "No backend s3 block found"
        assert re.search(r'region\s*=', block), (
            "Backend S3 block does not specify a 'region'"
        )

    def test_ac_010_2_dynamodb_locking(self, all_terraform_source):
        """AC-010-2: DynamoDB table is specified for state locking."""
        block = self._find_backend_block(all_terraform_source)
        assert block is not None, "No backend s3 block found"
        assert re.search(r'dynamodb_table\s*=', block), (
            "Backend S3 block does not specify 'dynamodb_table' for state locking"
        )

    def test_ac_010_3_backend_encryption(self, all_terraform_source):
        """AC-010-3: Backend encryption is enabled."""
        block = self._find_backend_block(all_terraform_source)
        assert block is not None, "No backend s3 block found"
        assert re.search(r'encrypt\s*=\s*true', block), (
            "Backend S3 block does not have 'encrypt = true'"
        )
