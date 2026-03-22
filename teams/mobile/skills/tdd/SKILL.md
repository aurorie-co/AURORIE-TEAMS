# TDD Skill (Mobile)

Use when writing any new mobile code, fixing bugs, or filling test coverage gaps.

## When to Use
- Any new screen, component, ViewModel, or service
- Any bug fix — write a failing test reproducing the bug first
- Any refactor that changes behavior

## Process

### 1. Write the Failing Test First
Before any implementation:
- Identify the smallest testable unit of behavior.
- Write a test that calls the not-yet-existing code and asserts the expected result.
- The test must fail at this point (confirm by running it).

**iOS — XCTest:**
```swift
func test_loginViewModel_withValidCredentials_setsIsLoggedInToTrue() {
    // Given
    let sut = LoginViewModel(authService: MockAuthService())
    // When
    sut.login(email: "user@example.com", password: "correctpassword")
    // Then
    XCTAssertTrue(sut.isLoggedIn)
}
```

**Android — JUnit + Turbine (for Flow testing):**
```kotlin
@Test
fun `login with valid credentials sets isLoggedIn to true`() = runTest {
    // Given
    val viewModel = LoginViewModel(FakeAuthRepository())
    // When
    viewModel.login("user@example.com", "correctpassword")
    // Then
    val state = viewModel.uiState.value
    assertTrue(state.isLoggedIn)
}
```

### 2. Run the Test — Confirm it Fails
- iOS: `⌘U` in Xcode or `xcodebuild test -scheme <scheme>`
- Android: `./gradlew test` (unit) or `./gradlew connectedAndroidTest` (instrumented)

A test that passes before the implementation is written is not a useful test.

### 3. Write Minimal Implementation
Write only enough code to make the test pass. Resist adding "what if" cases not yet covered by a test.

### 4. Run the Test — Confirm it Passes
Confirm it passes. If it doesn't, fix the implementation — not the test.

### 5. Check for Regressions
Run the full test suite. Confirm no previously passing tests now fail.

### 6. Refactor (Optional)
If the implementation has obvious duplication or poor readability, refactor now while tests are green.

### 7. Repeat for the Next Behavior

## Test Quality Guidelines
- **Unit tests**: test one ViewModel / service / use case in isolation; mock/fake dependencies.
- **UI tests (XCUITest / Espresso / Compose)**: test critical user flows end-to-end; use sparingly (slow).
- Each test should have exactly one reason to fail.
- Test names describe behavior: `test_loginViewModel_withExpiredToken_showsErrorMessage`, not `testLogin2`.
- Use specific assertions (`XCTAssertEqual`, `assertEquals`) not generic booleans (`XCTAssertTrue(x == y)`).

## Coverage Expectations
- New features: 80%+ line coverage on new ViewModel/service code.
- Bug fixes: the regression test reproducing the bug is mandatory.
- Skip coverage for: generated code, simple data classes/structs, AppDelegate boilerplate.
