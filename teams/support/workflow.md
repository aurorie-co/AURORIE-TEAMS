# Support Workflow

## Ticket Response
Trigger: incoming customer ticket or support request

Steps:
1. support-lead receives ticket and assigns triage
2. support-triage classifies issue and sets priority
3. support-responder drafts customer response
4. Write output to `.claude/workspace/artifacts/support/<task-id>/`

## Escalation Handling
Trigger: high-priority or complex issue requiring cross-team coordination

Steps:
1. support-lead routes to support-escalation
2. support-escalation coordinates with relevant teams and drafts resolution plan
3. Write output to `.claude/workspace/artifacts/support/<task-id>/`
