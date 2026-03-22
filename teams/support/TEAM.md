# Support Team

## Responsibility
Owns customer support, ticket triage, and issue response.
Does not own product decisions or engineering fixes.

## Agents
| Agent | Role |
|-------|------|
| support-lead | Task intake and internal routing |
| support-triage | Issue classification and prioritization |
| support-responder | Customer response drafting |
| support-escalation | Escalation handling and coordination |

## Input Contract
Provide: customer message or ticket, any relevant account context, priority level.

## Output Contract
Writes artifacts to `.claude/workspace/artifacts/support/<task-id>/`.
Returns response drafts and triage notes via Agent tool response.
