# Market Workflow

## Content Creation
Trigger: blog post, landing page, social media, email campaign request

Steps:
1. aurorie-market-lead reads the brief: audience, goal, format, tone, keywords if provided.
2. If SEO optimization is requested: dispatch aurorie-market-seo first to produce keyword and on-page guidance.
3. Dispatch aurorie-market-content with the brief and any SEO guidance as `artifact:` in `input_context`.
4. aurorie-market-content drafts the content using `content-engine` skill.
5. aurorie-market-lead reviews: does it match the brief? Is the CTA clear? Is the tone correct?
6. aurorie-market-lead writes `market-summary.md` with: deliverable summary, target keywords used, word count.

## SEO Audit
Trigger: site audit request, page ranking analysis, or technical SEO review

Steps:
1. aurorie-market-lead defines scope: full site audit or specific page(s).
2. Dispatch aurorie-market-seo with URL(s) and any known ranking goals.
3. aurorie-market-seo applies `seo-audit` skill: technical → on-page → off-page analysis.
4. aurorie-market-seo writes `seo-report.md` with prioritized recommendations.
5. aurorie-market-lead summarizes top-3 priority fixes for the requester.

## Campaign Analytics
Trigger: performance report request, campaign review, attribution analysis

Steps:
1. aurorie-market-lead identifies the time period, channels, and KPIs to analyze.
2. Dispatch aurorie-market-analytics with data sources or metric references in `input_context`.
3. aurorie-market-analytics performs analysis: trend, benchmark comparison, channel attribution.
4. aurorie-market-analytics writes `analytics-report.md` with: key findings, recommendations, next actions.
5. aurorie-market-lead summarizes the headline numbers and top recommendation.
