# Data Team

## Responsibility
Owns data analysis, reporting, pipeline engineering, and visualization.
Does not own product decisions, marketing campaigns, or application code.

## Agents
| Agent | Role |
|-------|------|
| aurorie-data-lead | Task intake, analysis scoping, and routing |
| aurorie-data-analyst | Ad-hoc analysis, hypothesis testing, metric deep dives |
| aurorie-data-pipeline | ETL design, data quality, pipeline documentation |
| aurorie-data-reporting | Dashboard specs, recurring reports, visualization guidance |

## Input Contract
Provide: the question to answer, available data sources, time period, relevant dimensions/filters.
For pipeline tasks: source schema, target schema, transformation logic, SLA requirements.
For reports: audience, frequency, key metrics, existing dashboard URLs if any.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/data/<task-id>/`.
- Analysis: `analysis.md` (findings, methodology, insights, recommendations)
- Pipeline: `pipeline-design.md` (architecture, transformations, data quality checks)
- Report: `report-spec.md` (metric definitions, chart specs, refresh schedule)
