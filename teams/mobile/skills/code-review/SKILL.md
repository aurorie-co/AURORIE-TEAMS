# Code Review Skill (Mobile)

Use when reviewing an iOS or Android PR, or validating a mobile implementation before sign-off.

## When to Use
- PR review requested
- Post-implementation quality check
- Store submission readiness check

## Review Order
Always review in this order — stop a category if blockers are found:

### 1. Crashes & Memory (Blockers)
**iOS:**
- [ ] No force-unwrap (`!`) on optionals that could be nil at runtime
- [ ] No retain cycles — escaping closures capture `[weak self]` or `[unowned self]`
- [ ] No use of deallocated objects (check async callbacks that reference `self`)

**Android:**
- [ ] No unsafe null assertions (`!!`) unless provably non-null
- [ ] No memory leaks — coroutine scopes tied to lifecycle (`viewModelScope`, `lifecycleScope`)
- [ ] No `Context` held beyond its lifecycle in long-lived objects

### 2. Correctness (Blockers / Majors)
- [ ] Logic matches the spec or ticket requirements
- [ ] All UI state changes happen on the main thread
- [ ] Permission denials handled gracefully — no crash or silent failure
- [ ] Edge cases: empty state, no network, slow network, large data sets
- [ ] Minimum supported OS version compatibility verified

### 3. Performance / Battery (Majors / Minors)
- [ ] No blocking calls on main thread
- [ ] No unnecessary background work — battery-heavy operations have justification
- [ ] Images loaded asynchronously and cached appropriately
- [ ] List views use cell reuse (iOS) / RecyclerView (Android) — no full re-creation per scroll

### 4. Maintainability (Minors / Suggestions)
- [ ] Follows MVVM: Views observe state; ViewModels hold logic; no business logic in Views
- [ ] No hardcoded strings that should be localized
- [ ] No magic numbers — use named constants
- [ ] Tests cover happy path and at least one failure/crash scenario

## Finding Severity
- **Blocker**: Must be fixed before merge. Crashes, data loss, policy violations.
- **Major**: Should be fixed before merge. Performance issues, unhandled permission denials.
- **Minor**: Fix in follow-up or quickly in this PR. Naming, minor logic simplifications.
- **Suggestion**: Optional. Architecture improvements, future refactors.

## Output
Write `code-review.md` with findings grouped by severity and platform (iOS / Android). Start with:
"Approved", "Approved with minor comments", or "Changes requested — see Blockers section."
