# Support Team

## Responsibility
Owns customer ticket triage, response drafting, and escalation coordination.
Does not own product decisions, engineering fixes, or billing policy changes.

## Agents
| Agent | Role |
|-------|------|
| aurorie-support-lead | Task intake, issue routing, and response quality review |
| aurorie-support-triage | Issue classification, priority scoring, and category assignment |
| aurorie-support-responder | Customer-facing response drafting and tone review |
| aurorie-support-escalation | Cross-team coordination for complex or high-priority issues |

## Input Contract
Provide: customer message or ticket text, account context (plan, tenure, recent activity if relevant),
any prior support history for this issue, and initial priority if known.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/support/<task-id>/`.
- Ticket Response: `triage-report.md` + `response-draft.md`
- Escalation Handling: `triage-report.md` + `escalation-plan.md` + `response-draft.md`
- Bulk / Pattern Response: `triage-report.md` + `response-draft.md`
- All workflows: `summary.md` (written by lead — ticket category, resolution approach, open follow-ups)
