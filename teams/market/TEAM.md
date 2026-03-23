# Market Team

## Responsibility
Owns marketing strategy, content creation, SEO, and campaign analytics.
Does not own product roadmap, engineering decisions, or customer support tickets.

## Agents
| Agent | Role |
|-------|------|
| aurorie-market-lead | Task intake, routing, and summary synthesis |
| aurorie-market-seo | SEO audits, keyword research, on-page optimization, competitor SEO |
| aurorie-market-content | Blog posts, social media copy, email campaigns, landing pages, multi-platform distribution |
| aurorie-market-analytics | Campaign performance, traffic reporting, attribution, growth opportunities |

## Input Contract
Provide: campaign goal, target audience, content type, existing materials or URLs to reference,
any performance benchmarks or KPIs to optimize toward.

## Output Contract
Artifacts written to `.claude/workspace/artifacts/market/<task-id>/`.
- Content Creation: `content.md` + `summary.md`
- SEO Audit: `seo-report.md` + `summary.md`
- Campaign Analytics: `analytics-report.md` + `summary.md`
- Content Performance Rewrite: `analytics-report.md` + `seo-report.md` + `content.md` + `summary.md`
- All workflows: `summary.md` (written by lead — deliverable summary, top insight, recommended next action)
