# Deployment Skill (Mobile)

Use for every mobile build, distribution, or CI/CD pipeline change.

## When to Use
- Building and distributing to TestFlight or Play Store internal track
- Promoting a build to production (App Store / Play Store)
- Modifying signing configuration, Fastlane lanes, or CI pipeline

## Pre-Release Checklist
Complete all items before distributing:

- [ ] All tests pass in CI (green build on release branch)
- [ ] Code review approved (no open Blockers)
- [ ] Version number and build number correct (build number auto-incremented)
- [ ] Release notes / changelog written
- [ ] Privacy manifest updated (iOS 17+) if new APIs used
- [ ] Required permission usage strings present for any new permissions
- [ ] App tested on a real device (not only simulator/emulator)
- [ ] Minimum OS version compatibility verified

## iOS Distribution

### Build & Sign
```bash
# Via Fastlane (recommended)
fastlane match appstore         # sync signing certificates
fastlane gym --scheme MyApp     # build .ipa
```

### Distribute to TestFlight
```bash
fastlane pilot upload --ipa MyApp.ipa --skip_waiting_for_build_processing
```

### Promote to App Store
Via App Store Connect UI or:
```bash
fastlane deliver --force        # submit for review
```

### Version Bump
- `versionCode` equivalent: `CFBundleVersion` — auto-increment in CI using `agvtool`
- Marketing version: `CFBundleShortVersionString` — set manually per release

## Android Distribution

### Build
```bash
./gradlew bundleRelease          # AAB (preferred for Play Store)
./gradlew assembleRelease        # APK (for direct distribution)
```

### Sign
```bash
# Signing config in build.gradle reads from environment variables
# KEYSTORE_FILE, KEYSTORE_PASSWORD, KEY_ALIAS, KEY_PASSWORD
```

### Distribute to Play Internal Track
```bash
fastlane supply --aab app/build/outputs/bundle/release/app-release.aab \
  --track internal
```

### Promote to Production
Via Play Console UI or:
```bash
fastlane supply --track internal --rollout 0.1  # staged rollout
```

### Version Bump
- `versionCode`: auto-increment in CI
- `versionName`: set manually per release

## Post-Distribution Verification
- [ ] Build appears in TestFlight / Play Internal within 10 minutes
- [ ] Install and launch tested on a physical device from the distribution channel
- [ ] Crash reporting (Crashlytics / Sentry) shows no new crashes after install
- [ ] Key user flow works end-to-end

## Rollback Procedure
- iOS: re-distribute the previous `.ipa` via TestFlight; reject current App Store submission if in review
- Android: use Play Console to halt a staged rollout; re-promote the previous release to production

## Output
Write `devops-implementation.md` with: build number distributed, distribution steps taken, verification results, rollback instructions.
