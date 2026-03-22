# Mobile Workflow

## Feature Development
Trigger: new screen, component, or native feature for iOS and/or Android

Steps:
1. aurorie-mobile-lead reads task and `input_context`. If `artifact:` references a design spec, reads it.
2. aurorie-mobile-lead identifies target platform(s): iOS only / Android only / both.
3. For iOS only: dispatch aurorie-mobile-ios.
   For Android only: dispatch aurorie-mobile-android.
   For both: dispatch aurorie-mobile-ios AND aurorie-mobile-android in parallel.
4. Each specialist applies `tdd` skill: write unit/UI test first, then implement.
5. aurorie-mobile-qa validates: runs tests on target platforms, checks acceptance criteria.
6. aurorie-mobile-lead writes `implementation.md` synthesizing platform outputs.

## Bug Fix
Trigger: crash, layout regression, wrong behavior, platform-specific issue

Steps:
1. aurorie-mobile-lead reads the bug report. Identifies platform and layer (UI / logic / native API).
2. Dispatch the appropriate specialist (aurorie-mobile-ios or aurorie-mobile-android).
3. Specialist applies `tdd` skill: write a failing test reproducing the crash or behavior first, then fix.
4. aurorie-mobile-qa confirms: tests pass, no regression on affected OS versions.
5. aurorie-mobile-lead writes `fix.md`: platform, root cause, fix, test added.

## Code Review
Trigger: PR review request or platform-specific quality check

Steps:
1. aurorie-mobile-lead routes to aurorie-mobile-qa (default) or platform specialist (deep review).
2. Reviewer applies `code-review` skill with mobile emphasis: memory / battery / permissions → correctness → performance → maintainability.
3. Writes `code-review.md`: Blocker / Major / Minor / Suggestion.
4. aurorie-mobile-lead summarizes blockers.

## Deployment
Trigger: TestFlight build, Play Store internal track, or production release

Steps:
1. aurorie-mobile-lead confirms distribution target: TestFlight / App Store / Play Internal / Play Production.
2. aurorie-mobile-devops applies `deployment` skill: pre-release checklist → build → sign → distribute.
3. aurorie-mobile-qa runs smoke tests on distributed build before promoting to production.
4. aurorie-mobile-lead writes `devops-implementation.md`: build number, distribution steps, rollback plan.
