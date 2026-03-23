# Research Team

## Responsibility
Owns information gathering, competitive intelligence, market research, and synthesis.
Does not own strategic decisions, product roadmap, or marketing execution.

## Agents
| Agent | Role |
|-------|------|
| aurorie-research-lead | Task intake, research scoping, and routing |
| aurorie-research-web | Web research, source gathering, competitive data collection |
| aurorie-research-synthesizer | Report synthesis, comparison matrices, executive summaries |

## Prerequisites
- `EXA_API_KEY` environment variable required for `exa-search` skill (exa MCP server)
- `FIRECRAWL_API_KEY` environment variable required for `deep-research` skill (firecrawl MCP server)
- Both keys must be configured in `teams/research/mcp.json` before deploying this team

## Input Contract
Provide: the research question, context (why this is needed, what decision it informs),
any known sources to include or exclude, desired output format and depth.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/research/<task-id>/`.
- Quick Lookup: `research-notes.md` + `summary.md`
- Deep Research: `research-notes.md` + `research-report.md` + `summary.md`
- Comparison: `research-notes.md` + `comparison-matrix.md` + `summary.md`
- All workflows: `summary.md` (written by lead — key findings, confidence level, recommended next action)
