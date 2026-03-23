# Frontend Workflow

## Feature Development
Trigger: new UI component, page, layout, or client-side feature

Steps:
1. aurorie-frontend-lead reads task and `input_context`. If `artifact:` references a UX brief or design spec, reads it.
2. aurorie-frontend-lead identifies scope: new component, modify existing, full page, or client-side logic.
3. Dispatch aurorie-frontend-developer.
4. aurorie-frontend-developer applies `tdd` skill and `frontend-patterns` skill: write component test first, then implement.
5. aurorie-frontend-developer writes `frontend-implementation.md`: files changed, component API (props/events), test coverage, accessibility notes, performance notes.
6. aurorie-frontend-qa validates: runs tests, checks accessibility and responsiveness, writes `qa-report.md`. For critical user flows, writes E2E test using `e2e-testing` skill.
7. aurorie-frontend-lead reviews qa-report. If blockers exist, re-dispatch developer. If clear, writes `summary.md`: what was built, component API summary, QA outcome, any known limitations.

## Bug Fix
Trigger: UI rendering error, broken interaction, accessibility failure, layout regression

Steps:
1. aurorie-frontend-lead reads the bug report. Notes browser, OS, viewport size, and reproduction steps.
2. Dispatch aurorie-frontend-developer with full context.
3. aurorie-frontend-developer applies `tdd` skill: write failing test reproducing the bug first, then fix.
4. aurorie-frontend-developer writes `fix.md`: root cause, fix applied, test added, browsers verified.
5. aurorie-frontend-qa confirms: tests pass, no visual regression in target browsers. Updates `qa-report.md`.
6. aurorie-frontend-lead reviews. If regression found, re-dispatch developer. If clear, writes `summary.md`: root cause, fix summary, regression test added, browsers confirmed.

## Code Review
Trigger: PR review request or accessibility/performance audit

Steps:
1. aurorie-frontend-lead routes to aurorie-frontend-qa (primary) or aurorie-frontend-developer (deep logic review).
2. Reviewer applies `code-review` skill with frontend priorities: accessibility → security → correctness → performance → maintainability.
3. Writes `code-review.md` with findings using priority markers: 🔴 Blocker / 🟡 Suggestion / 💭 Nit.
4. aurorie-frontend-lead surfaces 🔴 Blockers to the requester. Blockers must be resolved before merge.
5. aurorie-frontend-lead writes `summary.md`: overall verdict (approve / request changes), blocker count, key findings, merge readiness.

## Deployment
Trigger: web deploy, CDN update, preview environment setup

Steps:
1. aurorie-frontend-lead confirms environment (preview / staging / production) and scope.
2. aurorie-frontend-devops applies `deployment` skill: pre-deploy checklist → build → deploy → verify. Measures and records bundle size delta.
3. aurorie-frontend-qa runs visual smoke test and Core Web Vitals check post-deploy.
4. aurorie-frontend-devops writes `devops-implementation.md`: what was deployed, bundle size delta, CDN cache strategy, verification status, rollback instructions.
5. aurorie-frontend-lead writes `summary.md`: environment deployed to, QA smoke test outcome, bundle size impact, rollback reference.
