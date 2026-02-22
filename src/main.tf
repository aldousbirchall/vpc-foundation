module "networking" {
  source               = "./modules/networking"
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
  environment          = var.environment
  project              = var.project
}

module "security" {
  source      = "./modules/security"
  vpc_id      = module.networking.vpc_id
  environment = var.environment
  project     = var.project
}

module "storage" {
  source      = "./modules/storage"
  bucket_name = var.bucket_name
  environment = var.environment
  project     = var.project
}
