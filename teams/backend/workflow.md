# Backend Workflow

## Feature Development
Trigger: new API endpoint, service logic, DB schema change, auth feature, background job

Steps:
1. aurorie-backend-lead reads task and `input_context`. If `artifact:` references a PRD or spec, reads it.
2. aurorie-backend-lead identifies the layer: endpoint, service, DB migration, auth, or background job.
3. Dispatch aurorie-backend-developer.
4. aurorie-backend-developer applies `tdd` skill: write failing test first, then implement.
5. aurorie-backend-qa validates: runs full test suite, checks acceptance criteria coverage, writes `qa-report.md`.
6. aurorie-backend-lead writes `backend-implementation.md` summarizing all changes, API contract, and how to test.

## Bug Fix
Trigger: API error, wrong business logic, DB corruption, auth bypass, failed background job

Steps:
1. aurorie-backend-lead reads the bug report. Identifies layer: endpoint / service / DB / auth.
2. Dispatch aurorie-backend-developer with full bug context.
3. aurorie-backend-developer applies `tdd` skill: write failing reproduction test first, then fix.
4. aurorie-backend-qa confirms fix: runs full test suite, verifies no regression.
5. aurorie-backend-lead writes `fix.md`: root cause, fix, test added, regression risk.

## Code Review
Trigger: PR review request or security-sensitive change

Steps:
1. aurorie-backend-lead routes to aurorie-backend-qa (default) or aurorie-backend-developer (deep logic review).
2. Reviewer applies `code-review` skill: security → correctness → performance → maintainability.
3. Writes `code-review.md` with findings: Blocker / Major / Minor / Suggestion.
4. aurorie-backend-lead summarizes blockers for the requester.

## Deployment
Trigger: deploy request, release, DB migration rollout

Steps:
1. aurorie-backend-lead confirms environment (staging / production) and scope.
2. aurorie-backend-devops applies `deployment` skill: pre-deploy checklist → deploy → verify.
3. aurorie-backend-qa runs post-deploy smoke tests.
4. aurorie-backend-lead writes `devops-implementation.md`: what was deployed, verification status, rollback instructions.
