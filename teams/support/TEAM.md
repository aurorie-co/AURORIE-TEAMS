# Support Team

## Responsibility
Owns customer ticket triage, response drafting, and escalation coordination.
Does not own product decisions, engineering fixes, or billing policy changes.

## Agents
| Agent | Role |
|-------|------|
| support-lead | Task intake, issue routing, and response quality review |
| support-triage | Issue classification, priority scoring, and category assignment |
| support-responder | Customer-facing response drafting and tone review |
| support-escalation | Cross-team coordination for complex or high-priority issues |

## Input Contract
Provide: customer message or ticket text, account context (plan, tenure, recent activity if relevant),
any prior support history for this issue, and initial priority if known.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/support/<task-id>/`.
- Triage: `triage-report.md` (category, priority, root cause hypothesis, routing decision)
- Response: `response-draft.md` (customer-facing response, tone notes, recommended send channel)
- Escalation: `escalation-plan.md` (issue summary, teams to involve, resolution steps, SLA)
