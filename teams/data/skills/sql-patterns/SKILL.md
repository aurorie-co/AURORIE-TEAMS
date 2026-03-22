# SQL Patterns Skill

Use when writing or reviewing any SQL query for analysis, reporting, or pipeline transformation.

## When to Use
- Any data analysis query
- Pipeline transformation SQL
- Metric definition SQL

## Query Structure (Preferred)

Use CTEs (Common Table Expressions) for multi-step logic. Avoid nested subqueries when a CTE is clearer.

```sql
-- Good: CTEs are readable and debuggable step by step
WITH
base AS (
  SELECT
    user_id,
    DATE_TRUNC('day', created_at) AS date,
    revenue
  FROM orders
  WHERE created_at >= '2024-01-01'
),
daily_revenue AS (
  SELECT
    date,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT user_id) AS unique_buyers
  FROM base
  GROUP BY date
)
SELECT * FROM daily_revenue ORDER BY date;
```

## Patterns

### Aggregation
```sql
-- Always use GROUP BY with all non-aggregate SELECT columns
SELECT
  category,
  DATE_TRUNC('month', created_at) AS month,
  COUNT(*) AS count,
  SUM(amount) AS total
FROM events
GROUP BY category, DATE_TRUNC('month', created_at)
ORDER BY month, category;
```

### Window Functions (for running totals, rankings, period-over-period)
```sql
-- Running total
SELECT
  date,
  revenue,
  SUM(revenue) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_revenue,

-- Period-over-period (current vs previous period)
  LAG(revenue, 7) OVER (ORDER BY date) AS revenue_7_days_ago,
  (revenue - LAG(revenue, 7) OVER (ORDER BY date)) / NULLIF(LAG(revenue, 7) OVER (ORDER BY date), 0) AS wow_growth
FROM daily_metrics;
```

### Deduplication
```sql
-- Keep the most recent row per user
WITH ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY updated_at DESC) AS rn
  FROM users
)
SELECT * FROM ranked WHERE rn = 1;
```

### NULL Handling
```sql
-- Use COALESCE for default values; use NULLIF to avoid divide-by-zero
SELECT
  COALESCE(revenue, 0) AS revenue,            -- replace NULL with 0
  revenue / NULLIF(visits, 0) AS revenue_per_visit  -- safe division
FROM metrics;
```

## Quality Rules
- [ ] Filter date ranges explicitly — never query unbounded tables
- [ ] Use `DISTINCT` only when duplicates are expected; do not use as a shortcut for incorrect JOINs
- [ ] JOIN type is explicit: `LEFT JOIN` when right side may be absent; `INNER JOIN` to require both
- [ ] Avoid `SELECT *` in production queries — list columns explicitly
- [ ] Add a comment above each CTE explaining what it produces
- [ ] Test on a small date range first before running on full dataset

## Performance Rules
- [ ] Filter on indexed columns in WHERE clauses (created_at, user_id, etc.)
- [ ] Avoid functions on indexed columns in WHERE: use `WHERE date >= '2024-01-01'` not `WHERE YEAR(date) = 2024`
- [ ] For large tables, add `LIMIT` during development; remove only after validating logic
