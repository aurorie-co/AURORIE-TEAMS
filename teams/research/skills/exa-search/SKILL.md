# Exa Search Skill

Use the `exa` MCP tool to run targeted web searches during research tasks.

## When to Use
- Any web search step in a research workflow
- Finding specific sources, companies, technologies, or people
- Checking recent developments on a topic

## Exa Search Patterns

### General Research Query
Keep queries specific and use natural-language questions rather than keyword strings.

**Good**: "What are the main differences between PostgreSQL and MySQL for OLAP workloads in 2024?"
**Bad**: "PostgreSQL MySQL OLAP comparison"

### Company / Competitor Research
```
"[company name] product overview and key features"
"[company name] pricing model and customer segments"
"[company name] funding and growth 2023 2024"
```

### Technology Assessment
```
"[technology] use cases and limitations production"
"[technology] vs [alternative] performance comparison"
"[technology] adoption trends enterprise 2024"
```

### Market Research
```
"[market segment] market size growth rate 2024"
"[market segment] key players competitive landscape"
"[market segment] customer pain points and buying criteria"
```

## Result Evaluation
After each search:
1. Scan the top 5 results. Are they on-topic? From credible sources?
2. If results are off-topic, refine the query: be more specific, add context, or reframe as a question.
3. Click into sources that look authoritative — use `firecrawl` MCP to read the full page when needed.
4. Note the date of each source. For fast-moving topics, prefer sources < 18 months old.

## When to Escalate to firecrawl
Use `firecrawl` MCP (not just Exa search summaries) when:
- A source seems to contain important detail that the search summary doesn't fully capture
- You need to extract a specific table, statistic, or quote with full context
- The source is a long-form report or documentation page

## Citation Format
After using Exa, cite results as:
```
[Claim]. Source: [Page title], [Organization], [URL], accessed [date].
```
