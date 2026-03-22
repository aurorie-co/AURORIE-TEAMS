# Code Review Skill (Frontend)

Use when reviewing a frontend PR, assessing component quality, or validating an implementation before sign-off.

## When to Use
- PR review requested
- Post-implementation quality check
- Accessibility or performance audit

## Review Order
Always review in this order — stop a category if blockers are found:

### 1. Accessibility (Blockers)
- [ ] Interactive elements are keyboard operable (focusable, activatable with Enter/Space)
- [ ] All images have meaningful `alt` text (or `alt=""` for decorative images)
- [ ] Form inputs have associated `<label>` elements or `aria-label`
- [ ] Color contrast meets WCAG AA (4.5:1 for normal text, 3:1 for large text)
- [ ] Focus is managed correctly on modals, drawers, and dynamic content
- [ ] No content conveyed by color alone

### 2. Correctness (Blockers / Majors)
- [ ] Logic matches the spec or design
- [ ] Component handles loading, error, and empty states
- [ ] Events and callbacks behave as documented in props/API
- [ ] No hardcoded data that should be dynamic

### 3. Performance (Majors / Minors)
- [ ] No unnecessary re-renders (check dependency arrays in hooks, memo usage)
- [ ] Images optimized and lazy-loaded where appropriate
- [ ] No large dependencies imported for trivial use (check bundle impact)
- [ ] Expensive computations memoized if called frequently

### 4. Maintainability (Minors / Suggestions)
- [ ] Component does one thing; under ~150 lines
- [ ] No inline styles (use CSS modules / utility classes / design tokens)
- [ ] No `console.log` left in code
- [ ] No magic strings or hardcoded breakpoints — use named constants
- [ ] Tests cover happy path and at least one edge case

## Finding Severity
- **Blocker**: Must be fixed before merge. Accessibility failures, spec violations, broken states.
- **Major**: Should be fixed before merge. Performance regressions, missing error handling.
- **Minor**: Fix in follow-up or in this PR if quick. Naming, style inconsistencies.
- **Suggestion**: Optional improvement. Architecture, future improvements.

## Output
Write `code-review.md` with findings grouped by severity. Start with a one-sentence summary verdict:
"Approved", "Approved with minor comments", or "Changes requested — see Blockers section."
