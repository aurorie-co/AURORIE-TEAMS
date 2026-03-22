# Product Workflow

## Feature Definition
Trigger: new feature request, idea, or initiative from stakeholders

Steps:
1. product-lead reads the request. Asks: Is this well-scoped? Is the problem clear?
   If not, asks one clarifying question before proceeding.
2. Dispatch product-pm to write the PRD (using `prd-writing` skill).
3. If user experience is a significant part of the feature, dispatch product-ux in parallel.
4. product-pm writes `prd.md` with: problem statement, goals, user stories, requirements, success metrics.
5. product-ux (if dispatched) writes `ux-brief.md` with: user journey, key flows, interaction notes.
6. product-lead reviews both artifacts: are goals measurable? Are requirements implementable?
   Writes `product-summary.md` linking to both artifacts.

## User Story Writing
Trigger: backlog creation, sprint planning prep, or feature breakdown request

Steps:
1. product-lead defines the scope: which feature or epic to decompose.
2. Dispatch product-pm with the feature description and any existing PRD as `artifact:`.
3. product-pm applies `user-story` skill: writes stories in As a / I want / So that format with acceptance criteria.
4. product-pm prioritizes stories using MoSCoW: Must / Should / Could / Won't.
5. Output: `user-stories.md` with prioritized story list.

## UX Research Synthesis
Trigger: user feedback analysis, usability review, or design decision support

Steps:
1. product-lead provides user feedback data or research notes in `input_context`.
2. Dispatch product-ux.
3. product-ux synthesizes themes, identifies pain points, and maps user journeys.
4. Writes `ux-brief.md` with: user segments, pain points, opportunity areas, recommended flows.
5. product-lead summarizes top 3 user insights for the requester.
