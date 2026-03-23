# Research Workflow

## Deep Research
Trigger: research question, market study, competitive analysis, or investigation task

Steps:
1. aurorie-research-lead reads the question. Confirms: what decision will this inform? What depth is needed?
   If the question is too vague to scope (e.g., "research AI" with no focus), return `FAILED: ` requesting a specific question and decision context.
   Scope: "quick overview" → Quick Lookup workflow; "comprehensive report" → this workflow.
2. Dispatch aurorie-research-web with the research question and scope.
3. aurorie-research-web applies `exa-search` and `deep-research` skills to gather and validate sources.
4. aurorie-research-web writes `research-notes.md`: topic-organized findings with citations for each claim.
5. Dispatch aurorie-research-synthesizer with `artifact: research-notes.md` in `input_context`.
6. aurorie-research-synthesizer applies `market-research` skill when notes cover market sizing, competitor comparisons, investor diligence, or technology landscape scans. Identifies themes, distinguishes known vs. uncertain vs. contested findings.
7. aurorie-research-synthesizer writes `research-report.md`: executive summary (max 200 words), key findings, analysis, recommendations, confidence level.
8. aurorie-research-lead reviews: does the report answer the original question? Are there material unexplained gaps?
   If material gaps found (max one re-dispatch): re-dispatch aurorie-research-web with targeted follow-up questions, then re-run synthesizer with the updated notes.
   If gaps remain after one re-dispatch: document them in `summary.md` as known limitations and proceed.
9. aurorie-research-lead writes `summary.md`: what was found, confidence level, known gaps, recommended next action.

## Quick Lookup
Trigger: factual question, specific data point, or quick competitive check

Steps:
1. aurorie-research-lead confirms this is a single-fact or narrow lookup. If scope expands, switch to Deep Research.
2. Dispatch aurorie-research-web only.
3. aurorie-research-web applies `exa-search` skill. Finds the answer, validates against 2+ sources.
4. aurorie-research-web writes `research-notes.md`: the answer and sources cited.
5. aurorie-research-lead writes `summary.md`: the answer, source confidence, any caveats.

## Comparison / Matrix
Trigger: compare multiple options, vendors, technologies, or strategies

Steps:
1. aurorie-research-lead defines comparison dimensions: what criteria matter for the decision? (list them explicitly).
   If no options or decision context are provided and meaningful criteria cannot be derived from the task, return `FAILED: ` requesting the options to compare and the criteria or decision that should guide the comparison.
2. Dispatch aurorie-research-web with the research question **and the explicit criteria list** included in `input_context`. Web agent must structure `research-notes.md` sections to match those criteria.
3. aurorie-research-web writes `research-notes.md`: one section per option with criterion-aligned data and citations.
4. Dispatch aurorie-research-synthesizer with `artifact: research-notes.md`.
5. aurorie-research-synthesizer builds `comparison-matrix.md`: criteria as rows, options as columns, data cells with source references, explicit gaps flagged, recommendation section with reasoning.
6. aurorie-research-lead reviews: are gaps acceptable or should web agent fill them? Writes `summary.md`: recommended option with rationale, key trade-offs, confidence level.
