terraform {
  backend "s3" {
    bucket         = "vpc-foundation-tfstate"
    key            = "vpc-foundation/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "vpc-foundation-tflock"
  }
}
