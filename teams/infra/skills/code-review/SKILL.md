# Code Review Skill

Use when reviewing a PR, assessing code quality, or validating an implementation before sign-off.

## When to Use
- PR review requested
- Post-implementation quality check
- Security-sensitive changes (auth, payments, user data)

## Review Order
Always review in this order — stop a category if blockers are found:

### 1. Security (Blockers)
- [ ] No secrets or credentials hardcoded (API keys, passwords, tokens)
- [ ] User input is validated and sanitized before use
- [ ] SQL queries use parameterized statements — no string interpolation
- [ ] Authentication checked on every protected endpoint
- [ ] Authorization (role/permission) checked, not just authentication
- [ ] No sensitive data (PII, passwords) logged or returned in error responses
- [ ] File uploads: type and size validated; files not served from a user-controlled path

### 2. Correctness (Blockers / Majors)
- [ ] Logic matches the spec or ticket requirements
- [ ] Edge cases handled: null/empty input, zero values, max values, concurrent access
- [ ] Error conditions return appropriate status codes and messages
- [ ] Database transactions used where operations must be atomic
- [ ] No off-by-one errors in loops or pagination

### 3. Performance (Majors / Minors)
- [ ] No N+1 queries (no DB queries inside loops)
- [ ] Expensive operations (network calls, DB queries) not repeated unnecessarily
- [ ] Large data sets paginated — no unbounded queries
- [ ] Caching used appropriately for expensive, read-heavy data

### 4. Maintainability (Minors / Suggestions)
- [ ] Functions/methods do one thing; under ~40 lines
- [ ] Variable and function names are descriptive
- [ ] No magic numbers — use named constants
- [ ] No dead code (commented-out blocks, unused variables)
- [ ] Tests cover the happy path and at least one failure case
- [ ] No test logic in production code

## Finding Severity
- **Blocker**: Must be fixed before merge. Security issues, data loss risk, spec violations.
- **Major**: Should be fixed before merge. Performance issues, missing error handling, low coverage.
- **Minor**: Fix in follow-up or in this PR if quick. Naming, small logic simplifications.
- **Suggestion**: Optional improvement, team discussion. Architecture thoughts, future improvements.

## Output
Write `code-review.md` with findings grouped by severity. Start with a one-sentence summary verdict:
"Approved", "Approved with minor comments", or "Changes requested — see Blockers section."
