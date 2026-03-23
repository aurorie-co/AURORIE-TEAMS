# Mobile Workflow

## Feature Development
Trigger: new screen, component, or native feature for iOS and/or Android

Steps:
1. aurorie-mobile-lead reads task and `input_context`. If `artifact:` references a design spec, reads it.
2. aurorie-mobile-lead identifies target platform(s): iOS only / Android only / both.
3. For iOS only: dispatch aurorie-mobile-ios.
   For Android only: dispatch aurorie-mobile-android.
   For both: dispatch aurorie-mobile-ios AND aurorie-mobile-android in parallel.
4. Each specialist applies platform skills and `tdd` skill: write test first, then implement.
5. iOS specialist writes `ios-implementation.md`; Android specialist writes `android-implementation.md`.
6. aurorie-mobile-qa validates: runs tests on target platforms, checks acceptance criteria, writes `qa-report.md`.
7. aurorie-mobile-lead reviews qa-report. If blockers exist, re-dispatch specialist. If clear, writes `summary.md`: platforms implemented, feature summary, QA outcome, known OS version constraints.

## Bug Fix
Trigger: crash, layout regression, wrong behavior, platform-specific issue

Steps:
1. aurorie-mobile-lead reads the bug report. Identifies platform and layer (UI / logic / native API / background).
2. Dispatch the appropriate specialist (aurorie-mobile-ios or aurorie-mobile-android) with full context.
3. Specialist applies `tdd` skill: write failing test reproducing the crash or behavior first, then fix.
4. Specialist writes `fix.md`: platform, root cause, fix applied, test added, OS versions verified.
5. aurorie-mobile-qa confirms: tests pass, no regression on affected OS versions. Updates `qa-report.md`.
6. aurorie-mobile-lead reviews. If regression found, re-dispatch specialist. If clear, writes `summary.md`: platform, root cause, fix summary, regression test added.

## Code Review
Trigger: PR review request or platform-specific quality check

Steps:
1. aurorie-mobile-lead routes to aurorie-mobile-qa (default) or platform specialist (deep logic review).
2. Reviewer applies `code-review` skill with mobile priorities: memory/battery/crashes → correctness → performance → maintainability.
3. Writes `code-review.md` with findings using priority markers: 🔴 Blocker / 🟡 Suggestion / 💭 Nit.
4. aurorie-mobile-lead surfaces 🔴 Blockers to the requester. Blockers must be resolved before merge.
5. aurorie-mobile-lead writes `summary.md`: overall verdict (approve / request changes), blocker count, key findings, platform(s) reviewed.

## Deployment
Trigger: TestFlight build, Play Store internal track, or production release

Steps:
1. aurorie-mobile-lead confirms distribution target (TestFlight / App Store / Play Internal / Play Production) and platform scope.
2. aurorie-mobile-devops applies `deployment` skill: pre-release checklist → build → sign → distribute → verify. Records app size delta.
3. aurorie-mobile-qa runs smoke tests on the distributed build (physical device preferred) before promoting to production.
4. aurorie-mobile-devops writes `devops-implementation.md`: build number, signing method, distribution steps, app size delta, rollback plan.
5. aurorie-mobile-lead writes `summary.md`: platform(s) released, distribution target, build number, QA smoke test outcome, rollback reference.
