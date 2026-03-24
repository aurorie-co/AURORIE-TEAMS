# IaC Reliability Review

Use when reviewing Terraform modules that provision stateful resources, compute, or networking.
Covers high availability, observability, backup, and recovery — the concerns that matter after `terraform apply`.

## When to Use
- Any module provisioning compute (EC2, EKS, ECS, GCE, AKS)
- Any module provisioning stateful resources (RDS, ElastiCache, S3, GCS, Blob Storage)
- Any module provisioning networking (VPC, load balancers, DNS)
- Post-engineer review when checking `infra-plan.md`

---

## 1. High Availability (🔴 Blocker for single-AZ production)

```hcl
# GOOD — resources distributed across availability zones
resource "aws_db_subnet_group" "main" {
  subnet_ids = data.aws_subnets.private.ids  # spans multiple AZs

  tags = { Name = "main-db-subnet" }
}

resource "aws_db_instance" "main" {
  multi_az               = true   # synchronous standby in second AZ
  db_subnet_group_name   = aws_db_subnet_group.main.name
  deletion_protection    = true
  skip_final_snapshot    = false
}

# GOOD — auto-scaling group spans multiple AZs
resource "aws_autoscaling_group" "app" {
  vpc_zone_identifier = data.aws_subnets.private.ids  # multi-AZ
  min_size            = 2
  max_size            = 10
  desired_capacity    = 2
}
```

Checklist:
- [ ] Compute: ASG / MIG spans at least 2 AZs; `min_size >= 2` in production
- [ ] Database: `multi_az = true` (RDS) or equivalent HA configuration
- [ ] Load balancer: `subnets` covers at least 2 AZs
- [ ] No single-instance databases without documented justification (dev only)

---

## 2. Health Checks and Readiness (🟡 Suggestion if missing)

```hcl
# GOOD — ELB health check on ASG
resource "aws_autoscaling_group" "app" {
  health_check_type         = "ELB"   # not EC2 — checks application, not just host
  health_check_grace_period = 300
}

# GOOD — target group health check
resource "aws_lb_target_group" "app" {
  health_check {
    enabled             = true
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
    matcher             = "200"
  }
}
```

Checklist:
- [ ] ASGs use `health_check_type = "ELB"` (not `EC2`) when behind a load balancer
- [ ] Load balancer target groups have a health check path configured
- [ ] Health check grace period is sufficient for application startup time
- [ ] RDS/ElastiCache have `performance_insights_enabled = true` (where available)

---

## 3. Monitoring and Alerting Resources (🟡 Suggestion; 🔴 Blocker for production)

Terraform modules that provision resources **must include** the monitoring resources alongside them.
An EC2 ASG without a CPU alarm is incomplete infrastructure.

```hcl
# GOOD — CloudWatch alarm co-located with the resource it monitors
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.service_name}-${var.environment}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 120
  statistic           = "Average"
  threshold           = 80
  alarm_actions       = [var.alert_sns_arn]
  ok_actions          = [var.alert_sns_arn]
  dimensions          = { AutoScalingGroupName = aws_autoscaling_group.app.name }
}

resource "aws_cloudwatch_metric_alarm" "db_connections" {
  alarm_name          = "${var.service_name}-${var.environment}-db-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 60
  statistic           = "Average"
  threshold           = var.db_max_connections * 0.8
  alarm_actions       = [var.alert_sns_arn]
  dimensions          = { DBInstanceIdentifier = aws_db_instance.main.id }
}
```

Checklist:
- [ ] CPU alarms present for all compute resources
- [ ] Memory / connection alarms present for databases (RDS, ElastiCache)
- [ ] Disk space alarms present for storage-bound instances
- [ ] Error rate / 5xx alarms present for load balancers
- [ ] All alarms have `alarm_actions` pointing to an SNS topic (not empty)
- [ ] Alert SNS ARN is a module input variable — not hardcoded

---

## 4. Backup and Disaster Recovery (🔴 Blocker for stateful production resources)

```hcl
# GOOD — RDS with backup and protection
resource "aws_db_instance" "main" {
  backup_retention_period   = 7            # 7-day point-in-time recovery
  backup_window             = "03:00-04:00"
  maintenance_window        = "Sun:04:00-Sun:05:00"
  deletion_protection       = true
  skip_final_snapshot       = false        # never skip in prod
  copy_tags_to_snapshot     = true

  final_snapshot_identifier = "${var.service_name}-${var.environment}-final"
}

# GOOD — S3 with versioning and lifecycle
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  rule {
    id     = "expire-old-versions"
    status = "Enabled"
    noncurrent_version_expiration { noncurrent_days = 90 }
  }
}
```

Checklist:
- [ ] RDS: `backup_retention_period >= 7`, `deletion_protection = true`, `skip_final_snapshot = false`
- [ ] S3: versioning enabled on buckets holding critical data
- [ ] S3: lifecycle rules prevent unbounded version accumulation
- [ ] ElastiCache: snapshotting enabled (`snapshot_retention_limit > 0`)
- [ ] EBS volumes: snapshot policy created via `aws_dlm_lifecycle_policy` or equivalent

---

## 5. Auto-Scaling (🟡 Suggestion)

```hcl
# GOOD — scaling policy based on actual load signals
resource "aws_autoscaling_policy" "scale_out" {
  name                   = "${var.service_name}-scale-out"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 60.0  # scale to maintain 60% avg CPU
  }
}
```

Checklist:
- [ ] ASGs have scaling policies — not just fixed `desired_capacity`
- [ ] Scaling policies use target tracking (not just simple/step scaling) where available
- [ ] `max_size` cap prevents runaway scaling costs
- [ ] Scale-in cooldown is set (prevents thrashing)

---

## 6. Capacity and Cost Visibility (💭 Nit)

Checklist:
- [ ] Instance types are variables, not hardcoded (allows right-sizing without code changes)
- [ ] Storage sizes are variables with documented defaults
- [ ] Over-provisioned instance types flagged: `db.r6g.4xlarge` for a dev environment is a cost blocker
- [ ] `lifecycle { prevent_destroy = true }` on critical stateful resources in production modules

---

## Output

Flag findings using 🔴 Blocker / 🟡 Suggestion / 💭 Nit in `review.md`.

Reliability blockers (single-AZ prod database, no backups, no alarms with empty actions) are the same severity as security blockers — they represent production risk, not just best-practice gaps.
