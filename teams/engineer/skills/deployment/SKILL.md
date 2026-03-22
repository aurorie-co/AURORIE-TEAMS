# Deployment Skill

Use for every deployment, pipeline change, or infrastructure modification.

## When to Use
- Deploying to any environment (staging, production)
- Modifying CI/CD pipelines
- Docker or infrastructure changes

## Pre-Deploy Checklist
Complete all items before deploying:

- [ ] All tests pass in CI (green build on the target branch)
- [ ] Code review approved (no open Blockers)
- [ ] DB migrations included and reviewed (no destructive column drops without deprecation period)
- [ ] Environment variables verified in target environment (secrets injected, not hardcoded)
- [ ] Dependent services healthy (check status page or health endpoint)
- [ ] Rollback plan documented (how to undo this deploy in < 10 minutes)
- [ ] For production: staging tested with real-like data

## Deploy Steps

### Application Deploy (container-based)
1. Build image: `docker build -t <image>:<version> .`
2. Tag with version and `latest`: `docker tag <image>:<version> <registry>/<image>:latest`
3. Push to registry: `docker push <registry>/<image>:<version>`
4. Update service: `docker-compose up -d <service>` or deploy to orchestrator (K8s, ECS, etc.)
5. Wait for health check to pass (check `/health` or equivalent endpoint).
6. Monitor error rate and latency for 5 minutes post-deploy.

### Database Migrations
1. Take a DB snapshot / backup before running migrations on production.
2. Run migration on staging first; verify data integrity.
3. Run on production: `<migration-command>` (check project `Makefile` or `README`).
4. Verify migration completed without errors.
5. Spot-check affected tables/columns.

### CI/CD Pipeline Changes
1. Test pipeline change on a feature branch; do not edit production pipeline directly.
2. Confirm the pipeline runs to completion on the branch.
3. Merge to main and confirm main pipeline passes.

## Post-Deploy Verification
- [ ] Health endpoint returns 200: `curl -f <base-url>/health`
- [ ] Key user flow works (manual smoke test or automated E2E)
- [ ] No spike in error rate (check logs or monitoring dashboard)
- [ ] No unexpected latency increase

## Rollback Procedure
Document in `devops-implementation.md` before deploying:
1. Which image/version to roll back to
2. Exact rollback command
3. Whether a DB rollback migration is needed (and if so, the migration command)

## Output
Write `devops-implementation.md` with: deploy steps taken, verification results, rollback instructions.
