# Frontend Workflow

## Feature Development
Trigger: new UI component, page, layout, or client-side feature

Steps:
1. aurorie-frontend-lead reads task and `input_context`. If `artifact:` references a UX brief or design spec, reads it.
2. aurorie-frontend-lead identifies scope: new component, modify existing, full page, or client-side logic.
3. Dispatch aurorie-frontend-developer.
4. aurorie-frontend-developer applies `tdd` skill: write component/unit test first, then implement.
5. aurorie-frontend-qa validates: runs tests, checks accessibility and responsiveness, writes `qa-report.md`.
6. aurorie-frontend-lead writes `frontend-implementation.md` summarizing changes, component API, and how to test.

## Bug Fix
Trigger: UI rendering error, broken interaction, accessibility failure, layout regression

Steps:
1. aurorie-frontend-lead reads the bug report. Notes browser, OS, and reproduction steps.
2. Dispatch aurorie-frontend-developer with full context.
3. aurorie-frontend-developer applies `tdd` skill: write failing test reproducing the bug first, then fix.
4. aurorie-frontend-qa confirms: tests pass, no visual regression in target browsers.
5. aurorie-frontend-lead writes `fix.md`: root cause, fix, test added.

## Code Review
Trigger: PR review request or accessibility/performance audit

Steps:
1. aurorie-frontend-lead routes to aurorie-frontend-qa (primary) or aurorie-frontend-developer (deep logic).
2. Reviewer applies `code-review` skill with frontend emphasis: accessibility → correctness → performance → maintainability.
3. Writes `code-review.md`: Blocker / Major / Minor / Suggestion.
4. aurorie-frontend-lead summarizes blockers for the requester.

## Deployment
Trigger: web deploy, CDN update, preview environment setup

Steps:
1. aurorie-frontend-lead confirms environment (preview / staging / production) and scope.
2. aurorie-frontend-devops applies `deployment` skill: pre-deploy checklist → build → deploy → verify.
3. aurorie-frontend-qa runs visual smoke test post-deploy.
4. aurorie-frontend-lead writes `devops-implementation.md`: what was deployed, verification, rollback.
