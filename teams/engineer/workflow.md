# Engineer Workflow

## Feature Development
Trigger: new feature request, user story, or PRD reference

Steps:
1. engineer-lead reads task description and `input_context`. If an `artifact:` line references a PRD, reads it.
2. engineer-lead assesses scope:
   - UI only → dispatch engineer-frontend
   - API/DB only → dispatch engineer-backend
   - Both → dispatch engineer-frontend AND engineer-backend in parallel
   - Infrastructure required → also dispatch engineer-devops
3. Each specialist uses the `tdd` skill: write failing test → implement → pass.
4. engineer-qa validates: runs tests, checks acceptance criteria coverage, writes `qa-report.md`.
5. engineer-lead writes `implementation.md` summarizing all changes and how to test.

## Bug Fix
Trigger: bug report, failing test, exception in production

Steps:
1. engineer-lead reads the bug description. Identifies which layer is affected (frontend / backend / infra).
2. Dispatches the responsible specialist with full bug context.
3. Specialist uses `tdd` skill: write a failing test that reproduces the bug first, then fix.
4. engineer-qa confirms the fix: runs full test suite, verifies no regression.
5. engineer-lead writes `fix.md`: root cause, fix approach, test added, regression risk.

## Code Review
Trigger: PR review request or code quality check

Steps:
1. engineer-lead assigns review to engineer-qa (primary) or domain specialist (for deep logic review).
2. Reviewer uses `code-review` skill: security → correctness → performance → maintainability.
3. Writes `code-review.md` with findings categorized as: Blocker / Major / Minor / Suggestion.
4. engineer-lead summarizes blockers for the requester.

## Deployment
Trigger: deploy request, release task

Steps:
1. engineer-lead confirms which environment (staging / production) and scope.
2. engineer-devops uses `deployment` skill: pre-deploy checklist → deploy → verify.
3. engineer-qa runs smoke tests post-deploy.
4. engineer-lead writes `deployment.md`: what was deployed, verification status, rollback instructions.
