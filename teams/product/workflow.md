# Product Workflow

## Feature Definition
Trigger: new feature request, idea, or initiative from stakeholders

Steps:
1. aurorie-product-lead reads the request. If no target user persona or business goal is provided, ask one clarifying question before dispatching.
   If still missing after clarification, return `FAILED: ` requesting the persona and business goal.
2. Dispatch aurorie-product-pm (PRD) and aurorie-product-ux (UX brief) in parallel.
   If market validation or competitive context is needed: also dispatch aurorie-product-researcher.
3. aurorie-product-pm applies `prd-writing` skill. Writes `prd.md`: problem statement, goals, user stories, requirements, success metrics, out-of-scope items, dependencies.
4. aurorie-product-ux writes `ux-brief.md`: persona, current journey, friction points, proposed journey, design constraints, key interaction patterns.
5. aurorie-product-researcher (if dispatched) writes `market-research.md`: competitive context, market signals, opportunity validation.
6. aurorie-product-lead reviews all artifacts:
   - Are goals measurable? Are requirements implementable?
   - Do the PRD persona and UX brief persona match?
   - Are any UX constraints in conflict with PRD requirements?
   If inconsistencies found: re-dispatch the relevant specialist with a correction note before writing summary.
7. aurorie-product-lead writes `summary.md`: feature summary, key requirements, UX direction, market context if available, recommended next action.

## User Story Writing
Trigger: backlog creation, sprint planning prep, or feature breakdown request

Steps:
1. aurorie-product-lead defines scope: which feature or epic to decompose.
2. Dispatch aurorie-product-pm with the feature description and any existing PRD as `artifact:`.
3. aurorie-product-pm applies `user-story` skill: writes INVEST-compliant stories in As a / I want / So that format with acceptance criteria.
4. aurorie-product-pm prioritizes using MoSCoW: Must / Should / Could / Won't.
5. aurorie-product-pm writes `user-stories.md` with prioritized story list.
6. aurorie-product-lead reviews: are all Must stories clearly defined? Writes `summary.md`: epic summary, story count by priority, key acceptance criteria, sprint readiness.

## Roadmap Prioritization
Trigger: feature ranking request, sprint planning for multiple candidates, "what should we build next"

Steps:
1. aurorie-product-lead collects candidate features from the task or `artifact:`.
2. If no prior research artifact is available (no `ux-research.md` or `market-research.md`), optionally dispatch aurorie-product-researcher first to source Reach/Impact estimates for RICE scoring. Pass the resulting artifact to the PM.
3. Dispatch aurorie-product-pm.
3. aurorie-product-pm scores each item using RICE (Reach × Impact × Confidence ÷ Effort), cross-checks with MoSCoW, identifies cross-team dependencies and delivery risks.
4. aurorie-product-pm writes `roadmap.md`: ranked feature list with scores, rationale, dependencies, recommended sprint assignments.
5. aurorie-product-lead reviews: does ranking align with business goals? Are high-risk dependencies called out?
6. aurorie-product-lead writes `summary.md`: top 3 priorities with rationale, dependency risks, recommended next sprint scope.

## UX Research Synthesis
Trigger: user feedback analysis, usability review, or design decision support

Steps:
1. aurorie-product-lead reads the task. Confirms research input is provided in `input_context` or `artifact:`.
   If no research data is provided, return `FAILED: ` requesting the data source.
2. Dispatch aurorie-product-researcher.
3. aurorie-product-researcher synthesizes themes, identifies pain points, maps user journeys. Writes `ux-research.md`: user segments, pain points ranked by frequency/impact, opportunity areas, recommended flows.
4. If redesign guidance is also needed: dispatch aurorie-product-ux with `artifact: ux-research.md`.
5. aurorie-product-ux writes `ux-brief.md` incorporating research findings.
6. aurorie-product-lead writes `summary.md`: top 3 user insights, recommended product changes, confidence level.

## Market Research
Trigger: competitive analysis, market sizing, trend scan, opportunity assessment

Steps:
1. aurorie-product-lead reads the task. Confirms the research question is specific enough for actionable output.
   If the question is too vague (e.g., "research our market" with no scope), return `FAILED: ` requesting a scoped question (e.g., specific competitors, market segment, or geographic scope).
2. Dispatch aurorie-product-researcher.
3. aurorie-product-researcher applies `market-research` and/or `deep-research` skills. Writes `market-research.md`: market sizing, competitor landscape, trends, opportunities, risks, and recommended decisions.
4. aurorie-product-lead reviews: are all claims cited? Are there contrarian views? Is there a clear recommendation?
5. aurorie-product-lead writes `summary.md`: market opportunity summary, top competitive risks, recommended strategic action.
