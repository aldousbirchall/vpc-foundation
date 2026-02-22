"""
Shared pytest fixtures for vpc-foundation holdout test suite.

Provides:
- plan_data: Parsed plan.json from terraform show -json
- terraform_files: Dict of .tf file contents for static analysis
- makefile_content: Contents of the Makefile for build target checks
"""
import json
import os
from pathlib import Path

import pytest

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
PLAN_JSON = SRC_DIR / "plan.json"


@pytest.fixture(scope="session")
def plan_data():
    """Load and parse the Terraform plan JSON output.

    Expects plan.json at ../src/plan.json relative to .holdout/.
    This is the output of: terraform show -json plan.bin > plan.json
    """
    if not PLAN_JSON.exists():
        pytest.skip(f"plan.json not found at {PLAN_JSON}")
    with open(PLAN_JSON, "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def planned_resources(plan_data):
    """Extract all planned resources as a flat list from plan.json.

    Handles both root_module.resources and child_modules[].resources[].
    Each item is a dict with keys: type, name, values, address, etc.
    """
    resources = []
    root = plan_data.get("planned_values", {}).get("root_module", {})

    # Root-level resources
    resources.extend(root.get("resources", []))

    # Child module resources
    for module in root.get("child_modules", []):
        resources.extend(module.get("resources", []))
        # Handle nested child modules (unlikely but defensive)
        for nested in module.get("child_modules", []):
            resources.extend(nested.get("resources", []))

    return resources


@pytest.fixture(scope="session")
def resources_by_type(planned_resources):
    """Group planned resources by their type.

    Returns a dict: {"aws_vpc": [resource, ...], "aws_subnet": [...], ...}
    """
    by_type = {}
    for r in planned_resources:
        rtype = r.get("type", "")
        by_type.setdefault(rtype, []).append(r)
    return by_type


@pytest.fixture(scope="session")
def resource_changes(plan_data):
    """Extract resource_changes from plan.json for change-level assertions.

    Each entry has: address, type, change.before, change.after, change.actions.
    """
    return plan_data.get("resource_changes", [])


@pytest.fixture(scope="session")
def configuration_block(plan_data):
    """Extract the configuration block from plan.json.

    Contains provider_config, root_module (variables, resources, outputs).
    """
    return plan_data.get("configuration", {})


@pytest.fixture(scope="session")
def terraform_files():
    """Read all .tf files from ../src/ for static analysis.

    Returns a dict: {"main.tf": "contents...", "variables.tf": "contents...", ...}
    """
    tf_files = {}
    if not SRC_DIR.exists():
        pytest.skip(f"Source directory not found at {SRC_DIR}")
    for tf_path in SRC_DIR.glob("*.tf"):
        tf_files[tf_path.name] = tf_path.read_text()
    if not tf_files:
        pytest.skip("No .tf files found in source directory")
    return tf_files


@pytest.fixture(scope="session")
def all_terraform_source(terraform_files):
    """Concatenated content of all .tf files for broad pattern searches."""
    return "\n".join(terraform_files.values())


@pytest.fixture(scope="session")
def makefile_content():
    """Read the Makefile from ../src/ for build target analysis."""
    makefile_path = SRC_DIR / "Makefile"
    if not makefile_path.exists():
        pytest.skip(f"Makefile not found at {makefile_path}")
    return makefile_path.read_text()


@pytest.fixture(scope="session")
def variables_config(configuration_block):
    """Extract variable definitions from the configuration block.

    Returns a dict: {"variable_name": {default, description, type, ...}, ...}
    """
    root = configuration_block.get("root_module", {})
    return root.get("variables", {})


@pytest.fixture(scope="session")
def provider_config(configuration_block):
    """Extract provider configuration from the configuration block."""
    return configuration_block.get("provider_config", {})
