# Support Workflow

## Ticket Response
Trigger: incoming customer ticket, support email, or in-app report

Steps:
1. support-lead reads the ticket. Confirms: what is the customer's core problem? Is context sufficient?
   If context is missing, note the gap — do not guess.
2. Dispatch support-triage with the full ticket text.
3. support-triage applies the triage framework: classify category, score priority, hypothesize root cause.
4. support-triage writes `triage-report.md`.
5. Dispatch support-responder with the triage report as `artifact:` in `input_context`.
6. support-responder applies `customer-comms` skill: tone, acknowledgment, solution or next step.
7. support-responder writes `response-draft.md`.
8. support-lead reviews for accuracy and tone. Flags any factual errors before sending.

## Escalation Handling
Trigger: P0 or P1 issue, data loss, security concern, or issue requiring engineering/legal involvement

Steps:
1. support-lead identifies that the issue exceeds support team scope.
2. Dispatch support-escalation with full ticket + triage report as `artifact:` in `input_context`.
3. support-escalation documents the issue, identifies which teams must be involved, and defines resolution steps.
4. support-escalation writes `escalation-plan.md` with: issue summary, affected users, teams to engage,
   recommended resolution steps, customer communication draft, SLA commitment.
5. support-lead reviews and sends the customer holding response via support-responder.

## Bulk / Pattern Response
Trigger: multiple tickets about the same issue, or repeated question pattern detected

Steps:
1. support-lead identifies the pattern: what is the recurring question or issue?
2. Dispatch support-triage to confirm the pattern and assess impact scope.
3. Dispatch support-responder to draft a canonical response template for the pattern.
4. support-responder applies `customer-comms` skill to ensure the template is reusable across tone contexts.
5. Writes `response-draft.md` as a parameterized template with `[CUSTOMER_NAME]`, `[PRODUCT]` placeholders.
