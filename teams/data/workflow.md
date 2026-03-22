# Data Workflow

## Ad-Hoc Analysis
Trigger: specific data question, metric investigation, or hypothesis to test

Steps:
1. aurorie-data-lead reads the question. Confirms: what metric(s), what time period, what dimensions, what decision will this inform?
2. Dispatch aurorie-data-analyst with the scoped question.
3. aurorie-data-analyst profiles the data first: row counts, null rates, cardinality, obvious anomalies.
4. aurorie-data-analyst follows the analysis framework: hypothesis → query → validate → insight.
5. aurorie-data-analyst applies `sql-patterns` skill for queries; flags any data quality issues found.
6. aurorie-data-analyst writes `analysis.md` with: question, methodology, key findings, confidence level, recommended action.
7. aurorie-data-lead reviews for logical consistency and clarity of recommendation. Writes `summary.md`: question answered, key finding in one sentence, confidence level, recommended action, any data quality caveats.

## Pipeline Design
Trigger: new data pipeline request, ETL design, or data integration task

Steps:
1. aurorie-data-lead confirms source and target schemas, transformation requirements, SLA, and downstream consumers.
2. Dispatch aurorie-data-pipeline.
3. aurorie-data-pipeline profiles the source: row counts, nullability, cardinality, update frequency.
4. Defines the layer model (Bronze → Silver → Gold or simplified), data contracts, and schema drift policy.
5. Maps field-level transformations with explicit null-handling rules.
6. Designs quality checks at every stage; defines quarantine rules for anomalous rows.
7. Confirms idempotency design (re-runs produce same result) and retry/alerting policy.
8. Applies `sql-patterns` skill (and `postgres-patterns` / `clickhouse-io` as appropriate) for transformation SQL.
9. Writes `pipeline-design.md` with full design.
10. aurorie-data-lead reviews for completeness and SLA realism. Writes `summary.md`: what the pipeline does, layer model used, SLA, data quality guarantees, open risks.

## Report / Dashboard
Trigger: recurring report request, dashboard creation, or metric definition task

Steps:
1. aurorie-data-lead clarifies: audience, frequency (daily/weekly/monthly), primary metric and dimensions.
2. Dispatch aurorie-data-analyst to validate that the underlying data supports the proposed metrics.
3. aurorie-data-analyst writes a short metric validation note (can be part of `analysis.md` or a brief inline note) confirming data completeness and freshness.
4. Dispatch aurorie-data-reporting with analyst's validation as context.
5. aurorie-data-reporting applies `visualization` skill: selects chart types, defines metric formulas.
6. Writes the SQL for each metric using `sql-patterns` skill.
7. Defines refresh schedule, caching strategy, and alert on stale data (if applicable).
8. Writes `report-spec.md` with: metric definitions, SQL per metric, chart specifications, refresh schedule.
9. aurorie-data-lead reviews. Writes `summary.md`: report name, audience, primary metric, refresh cadence, data source confirmed, any known limitations.

## Data Quality Investigation
Trigger: numbers look wrong, metric unexpectedly changed, pipeline produced suspicious output

Steps:
1. aurorie-data-lead scopes the investigation: which metric / table / time range is affected? What is the expected vs. actual value?
2. Dispatch aurorie-data-analyst with full context.
3. aurorie-data-analyst traces the data lineage: gold → silver → bronze → source. Identifies at which layer the discrepancy originates.
4. Checks for: null propagation, schema drift, deduplication failures, late-arriving data, filter logic errors, upstream source changes.
5. Quantifies impact: how many rows are affected, over what time range, which downstream metrics are compromised.
6. Writes `analysis.md` with: root cause, scope of impact, affected rows/time range, fix recommendation.
7. If the fix requires a pipeline change: aurorie-data-lead dispatches aurorie-data-pipeline with the analysis as artifact.
8. aurorie-data-pipeline implements the fix and, if needed, designs a backfill strategy.
9. aurorie-data-lead writes `summary.md`: what was wrong, root cause, how it was fixed, backfill scope, prevention measure added.
