# Support Workflow

## Ticket Response
Trigger: incoming customer ticket, support email, or in-app report

Steps:
1. aurorie-support-lead reads the ticket. Confirms: what is the customer's core problem? Is context sufficient?
   If ticket text is missing or too vague to classify, return `FAILED: ` requesting the full ticket text.
2. Dispatch aurorie-support-triage with the full ticket text.
3. aurorie-support-triage applies the triage framework: classify category, score priority, hypothesize root cause.
4. aurorie-support-triage writes `triage-report.md`.
5. Dispatch aurorie-support-responder with the triage report as `artifact:` in `input_context`.
6. aurorie-support-responder applies `customer-comms` skill: tone, acknowledgment, solution or next step.
7. aurorie-support-responder writes `response-draft.md`.
8. aurorie-support-lead reviews for accuracy and tone. Flags any factual errors before sending.
9. aurorie-support-lead writes `summary.md`: ticket category, priority, response approach, any open follow-up items.

## Escalation Handling
Trigger: P0 or P1 issue, data loss, security concern, or issue requiring engineering/legal involvement

Steps:
1. aurorie-support-lead identifies that the issue exceeds support team scope.
   If no ticket text or triage report is available, return `FAILED: ` requesting the ticket and triage output.
2. Dispatch aurorie-support-triage if triage has not already been completed for this ticket.
3. Dispatch aurorie-support-escalation with full ticket + triage report as `artifact:` in `input_context`.
4. aurorie-support-escalation documents the issue, identifies which teams must be involved, and defines resolution steps.
5. aurorie-support-escalation writes `escalation-plan.md` with: issue summary, affected users, teams to engage,
   recommended resolution steps, customer communication draft, SLA commitment.
6. Dispatch aurorie-support-responder with the escalation plan as `artifact:` to produce a P0/P1 holding response for the customer.
7. aurorie-support-lead reviews both artifacts for accuracy before any external communication.
8. aurorie-support-lead writes `summary.md`: escalation reason, teams engaged, resolution steps, customer update sent, next update due.

## Bulk / Pattern Response
Trigger: multiple tickets about the same issue, or repeated question pattern detected

Steps:
1. aurorie-support-lead identifies the pattern: what is the recurring question or issue?
   If fewer than 2 examples of the pattern are provided, return `FAILED: ` requesting at least 2 representative ticket examples.
2. Dispatch aurorie-support-triage to confirm the pattern and assess impact scope.
3. aurorie-support-triage writes `triage-report.md` with pattern summary and affected user estimate.
4. Dispatch aurorie-support-responder with the triage report as `artifact:` to draft a canonical response template.
5. aurorie-support-responder applies `customer-comms` skill to ensure the template is reusable across tone contexts.
6. aurorie-support-responder writes `response-draft.md` as a parameterized template with `[CUSTOMER_NAME]`, `[PRODUCT]` placeholders.
7. aurorie-support-lead reviews the template for accuracy, policy compliance, and tone.
8. aurorie-support-lead writes `summary.md`: pattern identified, estimated affected users, template produced, recommended distribution (knowledge base / macro / proactive outreach).
