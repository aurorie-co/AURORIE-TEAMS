# Mobile Team

## Responsibility
Owns native iOS (Swift) and Android (Kotlin) application development, testing, and deployment.
Does not own backend APIs, web frontend, or product requirements.

## Agents
| Agent | Role |
|-------|------|
| aurorie-mobile-lead | Task intake, platform routing, and output synthesis |
| aurorie-mobile-ios | iOS development in Swift — UIKit, SwiftUI, Xcode, App Store |
| aurorie-mobile-android | Android development in Kotlin — Jetpack, Compose, Gradle, Play Store |
| aurorie-mobile-devops | Mobile CI/CD — Fastlane, Xcode Cloud, GitHub Actions, app distribution |
| aurorie-mobile-qa | Unit tests, UI tests (XCTest / Espresso), regression validation, store readiness |

## Input Contract
Provide: task description, target platform(s) (iOS / Android / both), acceptance criteria.
For bug fixes: device model, OS version, reproduction steps, crash logs if available.
For features: design spec or UX brief (use `artifact:` line in `input_context`).

## Output Contract
Artifacts written to `.claude/workspace/artifacts/mobile/<task-id>/`.
- iOS features: `ios-implementation.md` (files changed, APIs used, test coverage)
- Android features: `android-implementation.md` (files changed, APIs used, test coverage)
- Bug fixes: `fix.md` (platform, root cause, solution, test added)
- Code reviews: `code-review.md` (findings by severity)
- Deployments: `devops-implementation.md` (pipeline changes, distribution steps, rollback)
