# Market Team

## Responsibility
Owns marketing strategy, content creation, SEO, and campaign analytics.
Does not own product roadmap, engineering decisions, or customer support tickets.

## Agents
| Agent | Role |
|-------|------|
| aurorie-market-lead | Task intake and routing to marketing specialists |
| aurorie-market-seo | SEO audits, keyword research, on-page optimization recommendations |
| aurorie-market-content | Blog posts, social media copy, email campaigns, landing page copy |
| aurorie-market-analytics | Campaign performance analysis, traffic reporting, attribution |

## Input Contract
Provide: campaign goal, target audience, content type, existing materials or URLs to reference,
any performance benchmarks or KPIs to optimize toward.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/market/<task-id>/`.
- SEO: `seo-report.md` (findings, recommendations, priority ranking)
- Content: `content.md` (final copy with title, body, meta description, CTA)
- Analytics: `analytics-report.md` (metrics, insights, recommendations)
