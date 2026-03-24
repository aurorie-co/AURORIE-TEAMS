# Terraform Patterns

Use when writing or modifying any Terraform module.

## When to Use
- Writing a new Terraform module
- Modifying existing `.tf` files
- Structuring a module for reuse
- Setting up remote state or provider configuration

## Module Structure

Every module gets its own directory. Standard layout:

```
terraform/
  main.tf          ← resource definitions
  variables.tf     ← input variable declarations
  outputs.tf       ← output value declarations
  versions.tf      ← required_providers + terraform version constraint
  README.md        ← usage example, inputs table, outputs table
```

Add `data.tf` for data source lookups when the file would otherwise clutter `main.tf`.

## variables.tf — Always Typed and Described

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod"
  }
}

variable "instance_count" {
  type        = number
  description = "Number of EC2 instances to launch"
  default     = 1
}

variable "tags" {
  type        = map(string)
  description = "Common tags to apply to all resources"
  default     = {}
}
```

Rules:
- Every variable must have `type` and `description`
- Use `default` only when there is a safe, sensible default
- Use `validation` blocks for constrained values (enums, patterns, ranges)
- Never use `type = any` — be explicit

## outputs.tf — Every Output Has a Description

```hcl
output "instance_id" {
  value       = aws_instance.app.id
  description = "EC2 instance ID for use by downstream modules"
}

output "private_ip" {
  value       = aws_instance.app.private_ip
  description = "Private IP address of the instance"
  sensitive   = false
}

output "connection_string" {
  value       = "postgresql://${aws_db_instance.main.address}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
  description = "PostgreSQL connection string (without credentials)"
  sensitive   = false
}
```

## versions.tf — Always Pin Providers

```hcl
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
```

Never use `version = "*"` or omit version constraints entirely.

## Remote State — Never Local

```hcl
terraform {
  backend "s3" {
    bucket         = "my-company-tfstate"
    key            = "services/api/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
  }
}
```

Rules:
- Always use a remote backend (S3, GCS, Terraform Cloud, etc.)
- Enable server-side encryption on the state bucket
- Use a DynamoDB table (or equivalent) for state locking
- Never commit `.terraform/` or `*.tfstate` files

## Reusable Resources — for_each Over count

```hcl
# GOOD: for_each with a meaningful key
resource "aws_s3_bucket" "logs" {
  for_each = toset(var.log_bucket_names)
  bucket   = each.key
}

# GOOD: for_each over a map
resource "aws_iam_user" "ci" {
  for_each = var.ci_users
  name     = each.key
}

# BAD: count with index — fragile, hard to add/remove items
resource "aws_s3_bucket" "logs" {
  count  = length(var.log_bucket_names)
  bucket = var.log_bucket_names[count.index]
}
```

Use `count` only for on/off toggles (`count = var.create_resource ? 1 : 0`).

## Naming Conventions

```hcl
# Use underscores in resource names, not hyphens
resource "aws_security_group" "web_server" { }   # GOOD
resource "aws_security_group" "web-server" { }   # BAD

# Prefix resource names with the module or service name
resource "aws_s3_bucket" "api_uploads" { }

# Use var.environment and var.name_prefix for cloud resource names
resource "aws_s3_bucket" "uploads" {
  bucket = "${var.name_prefix}-${var.environment}-uploads"
}
```

## No Hardcoded Values

```hcl
# BAD
resource "aws_instance" "app" {
  ami           = "ami-0abcdef1234567890"
  instance_type = "t3.micro"
}

# GOOD
resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = var.instance_type
}
```

Exceptions: resource-type-specific constants that never change (`protocol = "tcp"`, `from_port = 443`).

## depends_on — Only When Implicit Dependency Fails

```hcl
# Terraform usually infers dependencies from resource references.
# Only use depends_on when the dependency is not expressed in the config.

resource "aws_s3_bucket_policy" "logs" {
  bucket = aws_s3_bucket.logs.id
  policy = data.aws_iam_policy_document.logs.json

  # Needed because the policy references a role created in the same plan
  depends_on = [aws_iam_role.log_writer]
}
```

## data Sources — Reference Existing Infrastructure

```hcl
data "aws_vpc" "main" {
  tags = {
    Name = "main-${var.environment}"
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }

  tags = {
    Tier = "private"
  }
}
```

## Formatting and Validation Checklist

Before handing off any Terraform:

- [ ] `terraform fmt` applied (consistent indentation and spacing)
- [ ] `terraform validate` passes (no syntax or reference errors)
- [ ] `terraform plan` reviewed (no unexpected destroy/replace operations)
- [ ] All variables have `type` and `description`
- [ ] All outputs have `description`
- [ ] Provider version constraints present in `versions.tf`
- [ ] Remote backend configured (no local state)
- [ ] No hardcoded account IDs, AMI IDs, secrets, or passwords
- [ ] `for_each` used for multi-instance resources (not `count` with index)
- [ ] Resource names use underscores, not hyphens
