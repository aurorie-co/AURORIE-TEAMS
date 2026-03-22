# Research Workflow

## Deep Research
Trigger: research question, market study, competitive analysis, or investigation task

Steps:
1. research-lead reads the question. Confirms: what decision will this inform? What depth is needed?
   Scope matters: "quick overview" → research-web only; "comprehensive report" → web then synthesizer.
2. Dispatch research-web with the research question and scope.
3. research-web applies `deep-research` and `exa-search` skills to gather and validate sources.
4. research-web writes `research-notes.md` with sourced, structured raw findings.
5. Dispatch research-synthesizer with `research-notes.md` as `artifact:` in `input_context`.
6. research-synthesizer reads the notes, identifies themes, applies synthesis methodology.
7. research-synthesizer writes `research-report.md` with: executive summary, key findings, analysis, recommendations.
8. research-lead reviews for completeness and flags any gaps.

## Quick Lookup
Trigger: factual question, specific data point, or quick competitive check

Steps:
1. research-lead assesses: is this a single-fact lookup or a multi-source question?
2. For single-fact: dispatch research-web only; skip synthesizer.
3. research-web searches, finds the answer, validates against 2 sources.
4. Writes `research-notes.md` with the answer and sources cited.

## Comparison / Matrix
Trigger: compare multiple options, vendors, technologies, or strategies

Steps:
1. research-lead defines the comparison dimensions (what criteria matter for the decision?).
2. Dispatch research-web to gather data on each option.
3. Dispatch research-synthesizer with `research-notes.md` as artifact.
4. research-synthesizer builds `comparison-matrix.md` and writes a recommendation section.
