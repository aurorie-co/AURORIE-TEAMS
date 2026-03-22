# SEO Audit Skill

Use when conducting any SEO analysis, keyword research, or on-page optimization review.

## When to Use
- Full site audit requested
- Individual page optimization
- Keyword research for new content
- Competitor SEO analysis

## Audit Order

### 1. Technical SEO
These affect crawlability and indexing — fix first:
- [ ] `robots.txt` allows important pages; blocks staging/admin
- [ ] XML sitemap exists and is linked in `robots.txt`
- [ ] No duplicate content (canonical tags set on paginated or multi-version pages)
- [ ] Page load speed: target < 3s on mobile (check Core Web Vitals: LCP, CLS, INP)
- [ ] HTTPS on all pages; no mixed content warnings
- [ ] Mobile-friendly: text readable without zoom, tap targets ≥ 48px
- [ ] Structured data (schema.org) present for key content types (Article, Product, FAQ)

### 2. On-Page SEO (per page)
- [ ] Title tag: 50-60 chars; primary keyword near the front; unique per page
- [ ] Meta description: 150-160 chars; includes keyword; has a clear benefit/CTA
- [ ] H1: one per page; includes primary keyword; matches search intent
- [ ] H2-H3: used hierarchically; include secondary keywords where natural
- [ ] Primary keyword in first 100 words of body
- [ ] Image alt text: descriptive; includes keyword where naturally relevant
- [ ] Internal links: 2-5 links to related content per page; use descriptive anchor text
- [ ] URL: short, lowercase, hyphenated, includes primary keyword; no unnecessary params

### 3. Keyword Analysis
1. Identify the primary keyword: what search query should this page rank for?
2. Check search intent: informational (how to, what is) / navigational (brand) / transactional (buy, pricing)
3. Assess competition: are the top results large authority sites or niche content?
4. Find long-tail variants: lower competition, more specific intent → often higher conversion
5. Topic cluster: which other pages on the site should link to this one? Which should it link to?

### 4. Prioritization
Rate each finding:
- **High**: Directly impacts rankings or crawlability (missing title, blocked by robots.txt, no HTTPS)
- **Medium**: Improves relevance or CTR (weak meta description, missing H1 keyword)
- **Low**: Polish and best-practice compliance (image alt text, structured data enrichment)

## Output Format in seo-report.md
```
## Executive Summary
[2-3 sentences: overall health, top 3 issues]

## Technical SEO Findings
[finding | severity | recommendation]

## On-Page Findings
[page | finding | severity | recommendation]

## Keyword Recommendations
[keyword | intent | competition | recommendation]

## Prioritized Action List
1. [High priority action] — estimated impact: [ranking/CTR/crawl]
...
```
