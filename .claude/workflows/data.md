# Data Workflow

## Ad-Hoc Analysis
Trigger: specific data question, metric investigation, or hypothesis to test

Steps:
1. aurorie-data-lead reads the question. Confirms: what metric(s), what time period, what dimensions, what decision will this inform?
2. Dispatch aurorie-data-analyst with the scoped question.
3. aurorie-data-analyst follows the analysis framework: hypothesis → query → validate → insight.
4. aurorie-data-analyst applies `sql-patterns` skill for queries; checks for data quality issues.
5. aurorie-data-analyst writes `analysis.md` with: question, methodology, key findings, confidence level, recommended action.
6. aurorie-data-lead reviews for logical consistency and clarity of recommendation.

## Pipeline Design
Trigger: new data pipeline request, ETL design, or data integration task

Steps:
1. aurorie-data-lead confirms source and target schemas, transformation requirements, and SLA.
2. Dispatch aurorie-data-pipeline.
3. aurorie-data-pipeline maps the data flow: source → transformation → target.
4. Applies `sql-patterns` skill for transformation logic.
5. Defines data quality checks at each stage.
6. Writes `pipeline-design.md` with: architecture diagram (text-based), transformation logic, data quality rules, monitoring approach.

## Report / Dashboard
Trigger: recurring report request, dashboard creation, or metric definition task

Steps:
1. aurorie-data-lead clarifies: audience, frequency (daily/weekly/monthly), primary metric and dimensions.
2. Dispatch aurorie-data-reporting, optionally with aurorie-data-analyst for metric validation.
3. aurorie-data-reporting applies `visualization` skill: selects chart types, defines metric formulas.
4. Writes `report-spec.md` with: metric definitions, SQL for each metric, chart specifications, refresh schedule.
5. aurorie-data-lead summarizes the report structure and key metrics for the requester.
