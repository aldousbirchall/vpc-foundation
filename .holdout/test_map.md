# Test Map: vpc-foundation

Maps every acceptance criterion to its corresponding test(s).

## Legend

| Category | File Pattern | Tool |
|---|---|---|
| Plan-parsing | `test_plan_REQ*.py` | pytest + plan.json |
| Policy | `test_policy_REQ*.py` | pytest + static analysis / plan.json |
| Terraform native | `test_REQ*_*.tftest.hcl` | terraform test + mock_provider |

---

## REQ-001: VPC Creation

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-001-1 | VPC CIDR 10.0.0.0/16 | `test_plan_REQ001_vpc.py` | `TestVPCCreation::test_ac_001_1_vpc_cidr` |
| AC-001-1 | VPC exists (native) | `test_REQ001_REQ006_networking.tftest.hcl` | `vpc_exists_with_correct_cidr` |
| AC-001-3 | DNS support enabled | `test_plan_REQ001_vpc.py` | `TestVPCCreation::test_ac_001_3_dns_support` |
| AC-001-4 | DNS hostnames enabled | `test_plan_REQ001_vpc.py` | `TestVPCCreation::test_ac_001_4_dns_hostnames` |
| AC-001-5 | VPC tags | `test_plan_REQ001_vpc.py` | `TestVPCCreation::test_ac_001_5_vpc_tags` |

## REQ-002: Public Subnets

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-002-1 | Public subnet eu-west-1a 10.0.1.0/24 | `test_plan_REQ002_public_subnets.py` | `TestPublicSubnets::test_ac_002_1_public_subnet_1a` |
| AC-002-2 | Public subnet eu-west-1b 10.0.2.0/24 | `test_plan_REQ002_public_subnets.py` | `TestPublicSubnets::test_ac_002_2_public_subnet_1b` |
| AC-002-3 | map_public_ip_on_launch enabled | `test_plan_REQ002_public_subnets.py` | `TestPublicSubnets::test_ac_002_3_public_ip_on_launch` |
| AC-002-4 | Public subnet tags | `test_plan_REQ002_public_subnets.py` | `TestPublicSubnets::test_ac_002_4_public_subnet_tags` |
| AC-002-* | Subnet count (native) | `test_REQ001_REQ006_networking.tftest.hcl` | `subnets_created` |

## REQ-003: Private Subnets

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-003-1 | Private subnet eu-west-1a 10.0.10.0/24 | `test_plan_REQ003_private_subnets.py` | `TestPrivateSubnets::test_ac_003_1_private_subnet_1a` |
| AC-003-2 | Private subnet eu-west-1b 10.0.20.0/24 | `test_plan_REQ003_private_subnets.py` | `TestPrivateSubnets::test_ac_003_2_private_subnet_1b` |
| AC-003-3 | No public IP on private subnets | `test_plan_REQ003_private_subnets.py` | `TestPrivateSubnets::test_ac_003_3_no_public_ip` |
| AC-003-4 | Private subnet tags | `test_plan_REQ003_private_subnets.py` | `TestPrivateSubnets::test_ac_003_4_private_subnet_tags` |

## REQ-004: Internet Gateway

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-004-1 | IGW exists | `test_plan_REQ004_internet_gateway.py` | `TestInternetGateway::test_ac_004_1_igw_exists` |
| AC-004-1 | IGW attached to VPC | `test_plan_REQ004_internet_gateway.py` | `TestInternetGateway::test_ac_004_1_igw_attached_to_vpc` |
| AC-004-1 | IGW exists (native) | `test_REQ001_REQ006_networking.tftest.hcl` | `internet_gateway_created` |
| AC-004-2 | IGW tags | `test_plan_REQ004_internet_gateway.py` | `TestInternetGateway::test_ac_004_2_igw_tags` |

## REQ-005: NAT Gateway

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-005-1 | NAT GW exists | `test_plan_REQ005_nat_gateway.py` | `TestNATGateway::test_ac_005_1_nat_gateway_exists` |
| AC-005-1 | Single NAT GW (cost) | `test_plan_REQ005_nat_gateway.py` | `TestNATGateway::test_ac_005_1_nat_single_az` |
| AC-005-1 | NAT GW exists (native) | `test_REQ001_REQ006_networking.tftest.hcl` | `nat_gateway_created` |
| AC-005-2 | EIP exists | `test_plan_REQ005_nat_gateway.py` | `TestNATGateway::test_ac_005_2_elastic_ip_exists` |
| AC-005-2 | NAT has allocation_id | `test_plan_REQ005_nat_gateway.py` | `TestNATGateway::test_ac_005_2_nat_has_allocation_id` |
| AC-005-2 | EIP exists (native) | `test_REQ001_REQ006_networking.tftest.hcl` | `elastic_ip_for_nat` |
| AC-005-3 | NAT GW tags | `test_plan_REQ005_nat_gateway.py` | `TestNATGateway::test_ac_005_3_nat_tags` |

## REQ-006: Route Tables

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-006-1 | Public route to IGW | `test_plan_REQ006_route_tables.py` | `TestRouteTables::test_ac_006_1_public_route_to_igw` |
| AC-006-2 | Public RT associations | `test_plan_REQ006_route_tables.py` | `TestRouteTables::test_ac_006_2_public_rt_associations` |
| AC-006-3 | Private route to NAT | `test_plan_REQ006_route_tables.py` | `TestRouteTables::test_ac_006_3_private_route_to_nat` |
| AC-006-4 | 4 total associations | `test_plan_REQ006_route_tables.py` | `TestRouteTables::test_ac_006_4_four_total_associations` |
| AC-006-5 | Route table tags | `test_plan_REQ006_route_tables.py` | `TestRouteTables::test_ac_006_5_route_table_tags` |
| AC-006-* | 2+ route tables (native) | `test_REQ001_REQ006_networking.tftest.hcl` | `route_tables_created` |
| AC-006-* | 4+ associations (native) | `test_REQ001_REQ006_networking.tftest.hcl` | `route_table_associations_created` |

## REQ-007: Web Tier Security Group

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-007-1 | Web SG exists | `test_plan_REQ007_web_security_group.py` | `TestWebSecurityGroup::test_ac_007_1_web_sg_exists` |
| AC-007-1 | 2+ SGs (native) | `test_REQ007_REQ008_security.tftest.hcl` | `security_groups_created` |
| AC-007-2 | Port 80 from 0.0.0.0/0 | `test_plan_REQ007_web_security_group.py` | `TestWebSecurityGroup::test_ac_007_2_port_80_ingress` |
| AC-007-3 | Port 443 from 0.0.0.0/0 | `test_plan_REQ007_web_security_group.py` | `TestWebSecurityGroup::test_ac_007_3_port_443_ingress` |
| AC-007-4 | Egress all | `test_plan_REQ007_web_security_group.py` | `TestWebSecurityGroup::test_ac_007_4_egress_all` |
| AC-007-5 | Web SG tags | `test_plan_REQ007_web_security_group.py` | `TestWebSecurityGroup::test_ac_007_5_web_sg_tags` |

## REQ-008: Application Tier Security Group

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-008-1 | App SG exists (2+ SGs) | `test_plan_REQ008_app_security_group.py` | `TestAppSecurityGroup::test_ac_008_1_at_least_two_sgs` |
| AC-008-2 | Ingress from web SG | `test_plan_REQ008_app_security_group.py` | `TestAppSecurityGroup::test_ac_008_2_ingress_from_web_sg` |
| AC-008-3 | No 0.0.0.0/0 on app SG | `test_plan_REQ008_app_security_group.py` | `TestAppSecurityGroup::test_ac_008_3_no_public_ingress_on_app_sg` |
| AC-008-4 | Egress all (both SGs) | `test_plan_REQ008_app_security_group.py` | `TestAppSecurityGroup::test_ac_008_4_app_sg_egress_all` |
| AC-008-5 | App SG tags | `test_plan_REQ008_app_security_group.py` | `TestAppSecurityGroup::test_ac_008_5_app_sg_tags` |

## REQ-009: S3 Bucket for Static Assets

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-009-1 | S3 bucket exists | `test_plan_REQ009_s3_bucket.py` | `TestS3Bucket::test_ac_009_1_s3_bucket_exists` |
| AC-009-1 | S3 exists (native) | `test_REQ009_storage.tftest.hcl` | `s3_bucket_created` |
| AC-009-2 | Versioning enabled | `test_plan_REQ009_s3_bucket.py` | `TestS3Bucket::test_ac_009_2_versioning_enabled` |
| AC-009-2 | Versioning resource (native) | `test_REQ009_storage.tftest.hcl` | `s3_versioning_configured` |
| AC-009-3 | AES256 encryption | `test_plan_REQ009_s3_bucket.py` | `TestS3Bucket::test_ac_009_3_encryption_aes256` |
| AC-009-3 | SSE resource (native) | `test_REQ009_storage.tftest.hcl` | `s3_encryption_configured` |
| AC-009-4 | Public access blocked (all 4) | `test_plan_REQ009_s3_bucket.py` | `TestS3Bucket::test_ac_009_4_public_access_blocked` |
| AC-009-4 | PAB resource (native) | `test_REQ009_storage.tftest.hcl` | `s3_public_access_block_created` |
| AC-009-5 | S3 bucket tags | `test_plan_REQ009_s3_bucket.py` | `TestS3Bucket::test_ac_009_5_s3_bucket_tags` |

## REQ-010: Remote State Backend

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-010-1 | Backend is S3 | `test_policy_REQ010_remote_state.py` | `TestRemoteStateBackend::test_ac_010_1_backend_is_s3` |
| AC-010-1 | Backend has bucket | `test_policy_REQ010_remote_state.py` | `TestRemoteStateBackend::test_ac_010_1_backend_has_bucket` |
| AC-010-1 | Backend has key | `test_policy_REQ010_remote_state.py` | `TestRemoteStateBackend::test_ac_010_1_backend_has_key` |
| AC-010-1 | Backend has region | `test_policy_REQ010_remote_state.py` | `TestRemoteStateBackend::test_ac_010_1_backend_has_region` |
| AC-010-2 | DynamoDB locking | `test_policy_REQ010_remote_state.py` | `TestRemoteStateBackend::test_ac_010_2_dynamodb_locking` |
| AC-010-3 | Backend encrypt = true | `test_policy_REQ010_remote_state.py` | `TestRemoteStateBackend::test_ac_010_3_backend_encryption` |

## REQ-011: Cost Constraints

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-011-1 | Single NAT GW | `test_policy_REQ011_cost.py` | `TestCostConstraints::test_ac_011_1_single_nat_gateway` |
| AC-011-1 | Single NAT (plan) | `test_plan_REQ005_nat_gateway.py` | `TestNATGateway::test_ac_005_1_nat_single_az` |
| AC-011-2 | No compute instances | `test_policy_REQ011_cost.py` | `TestCostConstraints::test_ac_011_2_no_compute_instances` |
| AC-011-2 | No compute (changes) | `test_policy_REQ011_cost.py` | `TestCostConstraints::test_ac_011_2_no_compute_in_resource_changes` |
| AC-011-2 | No compute (native) | `test_REQ007_REQ008_security.tftest.hcl` | `no_compute_instances` |
| AC-011-3 | Max instance size variable | `test_policy_REQ011_cost.py` | `TestCostConstraints::test_ac_011_3_max_instance_size_variable` |
| AC-011-4 | No expensive resources | `test_policy_REQ011_cost.py` | `TestCostConstraints::test_ac_011_4_no_expensive_resources` |

## REQ-012: Required Tagging

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-012-1 | default_tags in provider | `test_policy_REQ012_tags.py` | `TestRequiredTags::test_ac_012_1_default_tags_in_provider` |
| AC-012-2 | All resources tagged | `test_policy_REQ012_tags.py` | `TestRequiredTags::test_ac_012_2_all_taggable_resources_tagged` |
| AC-012-2 | Tag values non-empty | `test_policy_REQ012_tags.py` | `TestRequiredTags::test_ac_012_2_tag_values_not_empty` |

## REQ-013: Region Constraint

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-013-1 | Provider region set | `test_policy_REQ013_region.py` | `TestRegionConstraint::test_ac_013_1_provider_region` |
| AC-013-1 | Region is eu-west-1 | `test_policy_REQ013_region.py` | `TestRegionConstraint::test_ac_013_1_region_is_eu_west_1` |
| AC-013-2 | No other regions | `test_policy_REQ013_region.py` | `TestRegionConstraint::test_ac_013_2_no_other_regions` |
| AC-013-3 | Region variable exists | `test_policy_REQ013_region.py` | `TestRegionConstraint::test_ac_013_3_region_variable_exists` |
| AC-013-3 | Region default eu-west-1 | `test_policy_REQ013_region.py` | `TestRegionConstraint::test_ac_013_3_region_default_eu_west_1` |

## REQ-014: Encryption

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-014-1 | S3 AES256 encryption | `test_policy_REQ014_encryption.py` | `TestEncryption::test_ac_014_1_s3_encryption` |
| AC-014-2 | State backend encrypt | `test_policy_REQ014_encryption.py` | `TestEncryption::test_ac_014_2_state_backend_encrypted` |

## REQ-015: No Hardcoded Values

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-015-1 | Region is variable | `test_policy_REQ015_variables.py` | `TestVariableConfiguration::test_ac_015_1_region_is_variable` |
| AC-015-1 | AZs are variable | `test_policy_REQ015_variables.py` | `TestVariableConfiguration::test_ac_015_1_azs_are_variable` |
| AC-015-1 | CIDR is variable | `test_policy_REQ015_variables.py` | `TestVariableConfiguration::test_ac_015_1_cidr_is_variable` |
| AC-015-1 | Bucket name is variable | `test_policy_REQ015_variables.py` | `TestVariableConfiguration::test_ac_015_1_bucket_name_is_variable` |
| AC-015-2 | All vars have descriptions | `test_policy_REQ015_variables.py` | `TestVariableConfiguration::test_ac_015_2_all_variables_have_descriptions` |
| AC-015-3 | Region default | `test_policy_REQ015_variables.py` | `TestVariableConfiguration::test_ac_015_3_region_default` |
| AC-015-3 | AZ defaults | `test_policy_REQ015_variables.py` | `TestVariableConfiguration::test_ac_015_3_az_defaults_provided` |
| AC-015-3 | CIDR defaults | `test_policy_REQ015_variables.py` | `TestVariableConfiguration::test_ac_015_3_cidr_defaults_provided` |

## REQ-016: Terraform Plan Only

| AC | Description | Test File | Test Name |
|---|---|---|---|
| AC-016-1 | Makefile has init | `test_policy_REQ016_plan_only.py` | `TestPlanOnly::test_ac_016_1_makefile_has_init` |
| AC-016-1 | Makefile has validate | `test_policy_REQ016_plan_only.py` | `TestPlanOnly::test_ac_016_1_makefile_has_validate` |
| AC-016-1 | Makefile has plan | `test_policy_REQ016_plan_only.py` | `TestPlanOnly::test_ac_016_1_makefile_has_plan` |
| AC-016-2 | No apply target | `test_policy_REQ016_plan_only.py` | `TestPlanOnly::test_ac_016_2_no_apply_target` |
| AC-016-2 | No destroy target | `test_policy_REQ016_plan_only.py` | `TestPlanOnly::test_ac_016_2_no_destroy_target` |
| AC-016-2 | No terraform apply cmd | `test_policy_REQ016_plan_only.py` | `TestPlanOnly::test_no_terraform_apply_command` |
| AC-016-2 | No terraform destroy cmd | `test_policy_REQ016_plan_only.py` | `TestPlanOnly::test_no_terraform_destroy_command` |

---

## Coverage Summary

| Requirement | ACs | Tests | Covered |
|---|---|---|---|
| REQ-001 | 5 | 5 | AC-001-1, AC-001-3, AC-001-4, AC-001-5 (AC-001-2 covered by REQ-013) |
| REQ-002 | 4 | 5 | All |
| REQ-003 | 4 | 5 | All |
| REQ-004 | 2 | 3 | All |
| REQ-005 | 3 | 6 | All |
| REQ-006 | 5 | 8 | All |
| REQ-007 | 5 | 6 | All |
| REQ-008 | 5 | 5 | All |
| REQ-009 | 5 | 9 | All |
| REQ-010 | 4 | 6 | AC-010-1 through AC-010-3 (AC-010-4 = backend bucket versioning, out of plan scope) |
| REQ-011 | 4 | 6 | All |
| REQ-012 | 2 | 3 | All |
| REQ-013 | 3 | 5 | All |
| REQ-014 | 2 | 2 | All |
| REQ-015 | 3 | 9 | All |
| REQ-016 | 2 | 7 | All |
| **Total** | **58** | **90** | **All ACs covered** |

Note: AC-001-2 (VPC in eu-west-1) is implicitly covered by REQ-013 region constraint tests. AC-010-4 (backend bucket versioning) is an external prerequisite, not verifiable from the Terraform plan of this project.
