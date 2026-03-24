# IaC Security Review

Use when reviewing any Terraform module — new, modified, or audited from an existing codebase.

## When to Use
- Reviewing a PR containing `.tf` changes
- Auditing an existing Terraform codebase
- After writing a new module (self-review before handoff)
- Any time IAM, networking, storage, or secrets are involved

## Review Order

Work through these categories in order. Stop if Blockers are found — fix before continuing.

---

### 1. Secrets and Credentials (🔴 Blocker if found)

```hcl
# BAD — hardcoded secret
resource "aws_db_instance" "main" {
  password = "SuperSecret123"
}

# GOOD — variable with no default, injected at plan time
variable "db_password" {
  type        = string
  description = "Master password for the RDS instance"
  sensitive   = true
}

resource "aws_db_instance" "main" {
  password = var.db_password
}
```

Checklist:
- [ ] No hardcoded passwords, API keys, tokens, or account IDs in `.tf` files
- [ ] Sensitive variables marked `sensitive = true`
- [ ] Secrets injected via environment variables or secrets manager (not `terraform.tfvars` committed to git)
- [ ] State file backend has server-side encryption enabled (`encrypt = true`)

---

### 2. IAM Least Privilege (🔴 Blocker for wildcards)

```hcl
# BAD — wildcard actions and resources
resource "aws_iam_policy" "app" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}

# GOOD — scoped to specific actions and resource ARNs
resource "aws_iam_policy" "app" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject"]
      Resource = "arn:aws:s3:::${var.bucket_name}/*"
    }]
  })
}
```

Checklist:
- [ ] No `Action = "*"` without explicit documented justification
- [ ] No `Resource = "*"` without explicit documented justification
- [ ] IAM roles follow least-privilege — only permissions actually required
- [ ] Trust relationships scoped to specific principals (not `*`)
- [ ] IAM policies attached to roles, not users directly (where possible)

---

### 3. Network Exposure (🔴 Blocker for unintended public access)

```hcl
# BAD — security group open to the world
resource "aws_security_group_rule" "ingress" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]   # OPEN TO INTERNET
}

# GOOD — restricted to known CIDR or security group
resource "aws_security_group_rule" "ingress_ssh" {
  type                     = "ingress"
  from_port                = 22
  to_port                  = 22
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.bastion.id
}
```

Checklist:
- [ ] No security group rules with `0.0.0.0/0` or `::/0` on sensitive ports (22, 3389, 5432, 3306, 6379, 27017)
- [ ] S3 buckets: `block_public_acls = true`, `block_public_policy = true`, `ignore_public_acls = true`, `restrict_public_buckets = true` (unless explicitly a public website bucket)
- [ ] RDS, ElastiCache, and other data stores: `publicly_accessible = false`
- [ ] Load balancers: only HTTPS listeners in production (no plain HTTP on port 80 without redirect)
- [ ] VPC endpoints used for AWS service access where possible (avoids public internet traversal)

---

### 4. Encryption (🟡 Suggestion if missing, 🔴 Blocker for compliance scopes)

```hcl
# Storage — encryption at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

# RDS — encryption at rest
resource "aws_db_instance" "main" {
  storage_encrypted = true
  kms_key_id        = var.kms_key_arn
}

# In-transit — enforce TLS on load balancer
resource "aws_lb_listener" "http_redirect" {
  port     = 80
  protocol = "HTTP"
  default_action {
    type = "redirect"
    redirect { protocol = "HTTPS"; status_code = "HTTP_301" }
  }
}
```

Checklist:
- [ ] S3 buckets have server-side encryption enabled
- [ ] RDS instances have `storage_encrypted = true`
- [ ] EBS volumes have `encrypted = true`
- [ ] ElastiCache clusters have `at_rest_encryption_enabled = true` and `transit_encryption_enabled = true`
- [ ] Load balancers redirect HTTP → HTTPS

---

### 5. Cost Risks (🟡 Suggestion)

Checklist:
- [ ] No over-provisioned instance types (document why if `xlarge`+)
- [ ] S3 buckets have lifecycle rules to transition/expire old objects
- [ ] RDS: `deletion_protection = true` in prod; `skip_final_snapshot = false` in prod
- [ ] Auto Scaling groups have sensible `max_size` caps
- [ ] NAT Gateways: one per AZ is standard; flag if more are created without reason

---

### 6. State and Provider Hygiene (🔴 Blocker if local state)

Checklist:
- [ ] Remote backend configured (`s3`, `gcs`, `azurerm`, `cloud`) — no local state
- [ ] State locking enabled (DynamoDB for S3 backend, or native for others)
- [ ] All providers have version constraints in `versions.tf`
- [ ] `terraform_version` constraint set in `required_version`
- [ ] No `.terraform/` or `*.tfstate` files tracked by git (verify `.gitignore`)

---

### 7. Resource Tagging (💭 Nit)

```hcl
# All resources should carry common tags for cost attribution and ownership
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
    Team        = var.team
    Service     = var.service_name
  }
}

resource "aws_instance" "app" {
  tags = merge(local.common_tags, {
    Name = "${var.service_name}-${var.environment}"
  })
}
```

Checklist:
- [ ] Resources include `Environment`, `ManagedBy = "terraform"`, and at least one ownership tag
- [ ] Tag values use variables — not hardcoded strings

---

## Output Format

Write `review.md` using these markers:
- 🔴 **Blocker** — must be fixed before apply/merge
- 🟡 **Suggestion** — should be fixed; risk is lower but still real
- 💭 **Nit** — minor improvement, fix at discretion

Start with a one-line verdict:
`"Approved"` / `"Approved with suggestions"` / `"Changes required — see Blockers"`
