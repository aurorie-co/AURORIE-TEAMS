# PRD Writing Skill

Use when creating a Product Requirements Document, feature spec, or initiative brief.

## When to Use
- New feature or product initiative
- Significant change to existing feature
- Cross-team dependency requiring alignment

## PRD Template

Every PRD must contain all of the following sections:

```markdown
# PRD: [Feature Name]

**Status:** Draft | In Review | Approved
**Author:** aurorie-product-pm
**Date:** [ISO date]
**Version:** 1.0

---

## Problem Statement
[2-4 sentences: who has this problem, how often they encounter it, what they do today as a workaround, and why the workaround is insufficient.]

## Goals
What success looks like — from the user's perspective and the business's perspective:
- User goal: [what the user will be able to do]
- Business goal: [what metric improves]

## Non-Goals (Out of Scope)
Explicitly list what this PRD does NOT cover. This is as important as the goals.
- Not in scope: [item]

## User Personas
[Who is the primary user? One paragraph per persona if multiple.]

## Requirements

### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| F1 | [specific, testable statement] | Must |
| F2 | [specific, testable statement] | Should |

Priority: Must = required for launch / Should = important but not blocking / Could = nice to have

### Non-Functional Requirements
| Requirement | Target |
|-------------|--------|
| Performance | [e.g., page load < 2s, API response < 200ms p99] |
| Accessibility | [e.g., WCAG 2.1 AA] |
| Security | [e.g., PII fields encrypted at rest] |

## Success Metrics
How will we measure that this feature is working?
| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| [metric] | [current] | [goal] | [how to measure] |

## Dependencies
| Team | Dependency | Required By |
|------|------------|-------------|
| [team] | [what they need to build/provide] | [date or milestone] |

## Open Questions
- [question that needs resolution before development starts]
```

## Quality Rules
- Every requirement is testable: "The system shall X when Y" — not "The system should be fast".
- Every goal has a measurable success metric.
- Out-of-scope is filled in — never leave it blank.
- Open questions are resolved before engineering begins.
