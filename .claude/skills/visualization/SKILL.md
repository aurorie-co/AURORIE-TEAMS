# Visualization Skill

Use when choosing chart types, designing dashboards, or specifying visual reports.

## When to Use
- Any dashboard or report specification task
- Choosing how to present an analysis finding
- Defining chart configurations

## Chart Selection Guide

| Question type | Recommended chart | When to avoid |
|--------------|------------------|---------------|
| Trend over time | Line chart | When < 3 data points |
| Compare categories | Bar chart (horizontal if labels are long) | When > 10 categories — use table instead |
| Part of a whole | Stacked bar (multiple parts) or single donut (2-4 parts) | Never use pie for > 4 segments |
| Distribution | Histogram or box plot | Not bar chart — a bar chart is for categories |
| Correlation between two metrics | Scatter plot | Not meaningful for < 20 data points |
| Single important number | Big number / KPI card | Use this for the primary metric on every dashboard |
| Ranking | Sorted horizontal bar | Do not use pie or donut for ranking |
| Table with many dimensions | Data table with sorting | Don't force table data into a chart |

## Dashboard Design Principles

### Layout
1. **Top row**: Key KPI cards (3-4 big numbers that answer the primary question at a glance)
2. **Second row**: Primary trend chart (the "main story" — usually time-series of the primary metric)
3. **Remaining rows**: Supporting breakdowns and dimensions

### Color
- Use one accent color for the primary metric; grey for comparisons
- Red = bad / declining; Green = good / growing — be consistent
- Avoid rainbow palettes; use sequential (single hue) or diverging (two hues from a center)
- Ensure sufficient contrast for accessibility (4.5:1 ratio minimum)

### Labels and Titles
- Every chart has a title that states what it shows: "Weekly Revenue by Channel" not "Revenue"
- Y-axis label is always present; use human-readable units (K, M, %) not raw numbers when large
- Include a date range in the chart title or subtitle

### Common Mistakes to Avoid
- Truncated Y-axis: always start at zero for bar charts
- Dual-axis charts: almost always misleading — use two separate charts instead
- 3D charts: never — they distort perception
- Too many lines on a single line chart: > 5 lines → use small multiples or filter

## Output Format
When specifying a chart in `report-spec.md`:
```
Chart: [type] of [metric] by [dimension]
Title: "[Descriptive title]"
X-axis: [dimension with label]
Y-axis: [metric with unit]
Color: [what color encodes, if anything]
Filter: [any interactive filters this chart supports]
Why: [one sentence: what decision does this chart support]
```
