.PHONY: init fmt validate plan

init:
	terraform init -backend=false

fmt:
	terraform fmt -recursive

validate: init
	terraform validate

plan: init
	terraform plan
