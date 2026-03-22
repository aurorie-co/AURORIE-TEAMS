# User Story Skill

Use when writing user stories, backlog items, or acceptance criteria.

## When to Use
- Sprint backlog creation
- Feature decomposition
- Acceptance criteria definition

## Story Format (INVEST)
Each story must be:
- **I**ndependent: can be developed without another story being done first
- **N**egotiable: scope can be discussed
- **V**aluable: delivers value to the user on its own
- **E**stimable: engineer can estimate the effort
- **S**mall: completable in one sprint (< 5 days)
- **T**estable: acceptance criteria can be written as automated tests

## Story Template

```
**As a** [persona — be specific, not "user"]
**I want to** [action — one action per story]
**So that** [outcome — the value delivered]

**Acceptance Criteria:**
- Given [context], when [action], then [outcome]
- Given [context], when [action], then [outcome]
- Given [error condition], when [action], then [error is handled gracefully]

**Out of scope for this story:**
- [what is explicitly not included]
```

## Acceptance Criteria Format
Use Given / When / Then (Gherkin style):
- **Given**: the starting state or context
- **When**: the user action or system event
- **Then**: the expected result (observable and testable)

Every story needs at least:
1. The happy-path criterion
2. One error or edge case criterion

## MoSCoW Prioritization
When creating a story list, label each story:
- **Must**: required for launch — without this, the feature is incomplete
- **Should**: important but not blocking — include if time permits
- **Could**: nice to have — defer to next iteration
- **Won't**: explicitly out of scope for this release

## Story Map Output Format
```markdown
## Epic: [Feature Name]

### Must
- [ ] Story 1: As a [persona], I want to [action] so that [outcome]
  - AC: Given... when... then...

### Should
- [ ] Story 2: ...

### Could
- [ ] Story 3: ...
```
