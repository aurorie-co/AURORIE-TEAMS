# Research Team

## Responsibility
Owns information gathering, competitive intelligence, market research, and synthesis.
Does not own strategic decisions, product roadmap, or marketing execution.

## Agents
| Agent | Role |
|-------|------|
| research-lead | Task intake, research scoping, and routing |
| research-web | Web research, source gathering, competitive data collection |
| research-synthesizer | Report synthesis, comparison matrices, executive summaries |

## Input Contract
Provide: the research question, context (why this is needed, what decision it informs),
any known sources to include or exclude, desired output format and depth.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/research/<task-id>/`.
- Raw findings: `research-notes.md` (sourced, structured raw findings)
- Synthesis: `research-report.md` (synthesized findings, analysis, recommendations)
- Comparison: `comparison-matrix.md` (structured side-by-side comparison)
