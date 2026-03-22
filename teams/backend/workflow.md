# Backend Workflow

## Feature Development
Trigger: new API endpoint, service logic, DB schema change, auth feature, background job

Steps:
1. aurorie-backend-lead reads task and `input_context`. If `artifact:` references a PRD or spec, reads it.
2. aurorie-backend-lead identifies the layer: endpoint, service, DB migration, auth, or background job.
3. Dispatch aurorie-backend-developer.
4. aurorie-backend-developer applies `tdd` skill: write failing test first, then implement.
5. aurorie-backend-developer writes `backend-implementation.md`: files changed, API contract (endpoint, request/response shape), DB changes, security considerations, how to test.
6. aurorie-backend-qa validates: runs full test suite, checks acceptance criteria coverage, writes `qa-report.md`.
7. aurorie-backend-lead reviews qa-report. If blockers exist, re-dispatch developer. If clear, writes `summary.md`: what was built, API contract summary, DB changes, QA outcome, known limitations or follow-up items.

## Bug Fix
Trigger: API error, wrong business logic, DB corruption, auth bypass, failed background job

Steps:
1. aurorie-backend-lead reads the bug report. Identifies layer: endpoint / service / DB / auth.
2. Dispatch aurorie-backend-developer with full bug context.
3. aurorie-backend-developer applies `tdd` skill: write failing reproduction test first, then fix.
4. aurorie-backend-developer writes `fix.md`: root cause, fix applied, test added, regression risk.
5. aurorie-backend-qa confirms fix: runs full test suite, verifies no regression. Updates `qa-report.md`.
6. aurorie-backend-lead reviews. If regression found, re-dispatch developer. If clear, writes `summary.md`: root cause, fix summary, regression test added, any follow-up risk.

## Code Review
Trigger: PR review request or security-sensitive change

Steps:
1. aurorie-backend-lead routes to aurorie-backend-qa (default) or aurorie-backend-developer (deep logic review).
2. Reviewer applies `code-review` skill: security → correctness → performance → maintainability.
3. Writes `code-review.md` with findings using priority markers: 🔴 Blocker / 🟡 Suggestion / 💭 Nit.
4. aurorie-backend-lead surfaces 🔴 Blockers to the requester. Blockers must be resolved before merge.
5. aurorie-backend-lead writes `summary.md`: overall review verdict (approve / request changes), blocker count, key findings summary, merge readiness.

## Deployment
Trigger: deploy request, release, DB migration rollout

Steps:
1. aurorie-backend-lead confirms environment (staging / production), scope, and whether DB migrations are included.
2. aurorie-backend-devops applies `deployment` skill: pre-deploy checklist → choose rollout strategy (canary / blue-green / rolling) → deploy → verify.
3. aurorie-backend-qa runs post-deploy smoke tests against the live environment.
4. aurorie-backend-devops confirms: golden signals stable (latency, error rate, saturation), SLO burn rate not elevated. Writes `devops-implementation.md`: what was deployed, rollout strategy used, verification status, rollback instructions.
5. aurorie-backend-lead marks deployment complete or triggers rollback if signals degrade. Writes `summary.md`: environment deployed to, rollout strategy used, QA smoke test outcome, monitoring status, rollback instructions reference.
