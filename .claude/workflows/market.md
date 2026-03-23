# Market Workflow

## Content Creation
Trigger: blog post, landing page, social media copy, email campaign, ad copy request

Steps:
1. aurorie-market-lead reads the brief: audience, goal, format, tone, keywords if provided.
   If no audience or goal is provided, return `FAILED: ` requesting the target audience and campaign goal.
2. If content type is blog post or landing page: always dispatch aurorie-market-seo first to produce keyword and on-page guidance.
   For email or social copy: dispatch aurorie-market-seo only if SEO optimization is explicitly requested.
3. Dispatch aurorie-market-content with the brief and any SEO guidance as `artifact:` in `input_context`.
4. aurorie-market-content applies `content-engine` skill. Drafts content for each requested format.
   If multi-platform distribution is in scope: applies `crosspost` and `x-api` skills as appropriate.
   If distribution fails (API error, missing credentials): aurorie-market-content notes failed platforms in a `## Distribution Status` section in `content.md`. Content deliverable is still written and returned.
5. aurorie-market-content writes `content.md`: one labeled section per format/platform. Includes `## Distribution Status` section if distribution was attempted, noting which platforms succeeded and which failed with the reason.
6. aurorie-market-lead reviews: does it match the brief? Is the CTA clear? Is the tone correct? Does the content pass the `content-engine` quality checklist?
7. aurorie-market-lead writes `summary.md`: deliverable summary, formats produced, target keywords used, distribution platforms if applicable.

## SEO Audit
Trigger: site audit request, page ranking analysis, keyword research, or technical SEO review

Steps:
1. aurorie-market-lead defines scope: full site audit, specific page(s), keyword research only, or competitor SEO analysis.
   If no URL or topic is provided, return `FAILED: ` requesting the URL(s) or target keywords.
2. Dispatch aurorie-market-seo with URL(s) and any known ranking goals.
3. aurorie-market-seo applies `seo-audit` skill: technical → on-page → off-page → keyword analysis.
4. aurorie-market-seo writes `seo-report.md`: executive summary, findings by category (High/Medium/Low impact), prioritized action list.
5. aurorie-market-lead reviews: are the top-3 priorities actionable without engineering?
6. aurorie-market-lead writes `summary.md`: top-3 priority fixes, expected impact, recommended owner for each action.

## Campaign Analytics
Trigger: performance report request, campaign review, attribution analysis, channel ROI assessment

Steps:
1. aurorie-market-lead identifies: time period, channels (organic, paid, email, social), primary KPI.
   If no data source or metric reference is provided, return `FAILED: ` requesting the data input.
   Minimum data required: at least one metric with a current value and a comparison reference (prior period, target, or industry benchmark). If neither is available, return `FAILED: ` requesting a baseline for comparison.
2. Dispatch aurorie-market-analytics with data sources or metric references in `input_context`.
3. aurorie-market-analytics performs analysis: trend, benchmark comparison (applying `market-research` skill for industry data if needed), channel attribution, anomaly detection.
4. aurorie-market-analytics writes `analytics-report.md`: headline metrics table, key insights (observation → cause → recommendation), prioritized actions, growth opportunities.
5. aurorie-market-lead reviews: do recommendations tie back to the primary KPI?
6. aurorie-market-lead writes `summary.md`: headline performance verdict, top insight, top-1 recommended action, confidence level.

## Content Performance Rewrite
Trigger: "rewrite underperforming content", "improve content based on analytics", "content refresh", analytics-driven content update request

Steps:
1. aurorie-market-lead identifies: the underperforming content asset(s) and the performance data (traffic, conversions, rankings).
   If no content asset or performance data is provided, return `FAILED: ` requesting the asset URL/file and the metric showing underperformance.
2. Dispatch aurorie-market-analytics with the performance data to diagnose root cause (traffic drop, low CTR, high bounce, keyword ranking loss).
3. Dispatch aurorie-market-seo with the asset URL and analytics findings as `artifact:` to identify keyword and on-page gaps.
4. Dispatch aurorie-market-content with the original content, `analytics-report.md`, and `seo-report.md` as artifacts.
   aurorie-market-content rewrites the asset incorporating SEO fixes and analytics-driven improvements.
5. aurorie-market-content writes `content.md` with the rewritten asset clearly labeled as `## Rewrite: <asset name>` and a `## Changes Summary` section explaining what changed and why.
6. aurorie-market-lead reviews: does the rewrite address the root cause identified in analytics?
7. aurorie-market-lead writes `summary.md`: original performance issue, changes made, expected improvement, recommended A/B test if applicable.
