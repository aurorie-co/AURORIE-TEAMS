# TDD Skill

Use when writing any new code, fixing bugs, or filling test coverage gaps.

## When to Use
- Any new function, class, component, or API endpoint
- Any bug fix (write a failing test that reproduces the bug first)
- Any refactor that changes behavior

## Process

### 1. Write the Failing Test First
Before writing any implementation:
- Identify the smallest testable unit of behavior.
- Write a test that calls the not-yet-existing code and asserts the expected result.
- The test must fail at this point (confirm by running it).

**Test structure (xUnit style):**
```
given [context/state]
when [action is taken]
then [expected outcome]
```

### 2. Run the Test — Confirm it Fails
Run the test and confirm it fails with a meaningful error (e.g., "function not found", "assertion failed").
A test that passes before the implementation is written is not a useful test.

### 3. Write Minimal Implementation
Write only enough code to make the test pass. No extra logic, no premature abstraction.
Resist adding "what if" cases not covered by a test.

### 4. Run the Test — Confirm it Passes
Run the test again. Confirm it passes. If it doesn't, fix the implementation — not the test.

### 5. Check for Regressions
Run the full test suite. Confirm no previously passing tests now fail.

### 6. Refactor (Optional)
If the implementation has obvious duplication or poor readability, refactor now while tests are green.
Run tests again after refactoring.

### 7. Repeat for the Next Behavior
One behavior at a time. Add the next test only after the current one passes.

## Test Quality Guidelines
- **Unit tests**: test one function/method in isolation; mock external dependencies.
- **Integration tests**: test multiple layers working together (e.g., handler + database).
- **E2E tests**: test from the user's perspective; use sparingly (slow, brittle).
- Each test should have exactly one reason to fail.
- Test names should describe behavior: `test_user_cannot_login_with_wrong_password`, not `test_login_2`.
- Avoid generic boolean assertions (`assertTrue`, `expect(x).toBeTruthy()`) — use specific assertions that describe what you expect (`assertEqual`/`toBe`, `assertIn`/`toContain`, `assertRaises`/`toThrow`). Use the assertion style of your project's test framework.

## Coverage Expectations
- New features: 80%+ line coverage on the new code.
- Bug fixes: the regression test that reproduces the bug is mandatory.
- Skip coverage for: configuration files, generated code, simple data classes.
