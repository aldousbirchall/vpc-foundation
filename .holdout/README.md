# vpc-foundation Holdout Test Suite

Black-box test suite for the vpc-foundation infrastructure build. Tests validate requirements without referencing implementation details.

## Test Categories

### Terraform Native Tests (`.tftest.hcl`)
- `test_REQ001_REQ006_networking.tftest.hcl` -- VPC, subnets, gateways, route tables
- `test_REQ007_REQ008_security.tftest.hcl` -- Web and application security groups
- `test_REQ009_storage.tftest.hcl` -- S3 bucket and related resources

Run from `src/` with: `terraform test -test-directory=../.holdout/`

### Plan-Parsing Tests (`test_plan_*.py`)
Load `plan.json` and assert resource properties (CIDR blocks, tags, security group rules, S3 settings).

### Policy Tests (`test_policy_*.py`)
Enforce cost, compliance, and governance guardrails via static analysis of `.tf` source files and plan.json.

## Running

```bash
# Generate plan.json first (from src/):
cd ../src
terraform init
terraform plan -out=plan.bin
terraform show -json plan.bin > plan.json

# Run Python tests:
cd ../.holdout
pip install -r requirements.txt
pytest -v

# Run Terraform native tests (from src/):
cd ../src
terraform test -test-directory=../.holdout/
```

## Structure

- `conftest.py` -- Shared fixtures (plan_data, terraform_files, makefile_content)
- `test_map.md` -- Complete mapping of tests to requirement acceptance criteria
- `requirements.txt` -- Python dependencies (pytest only)
