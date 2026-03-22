# Deep Research Skill

Use for comprehensive, multi-source research requiring depth and coverage.

## When to Use
- Market research, competitive analysis, technology assessment
- Any question requiring more than 2-3 sources
- When confidence and coverage matter (not just finding an answer)

## Research Process

### 1. Define the Research Scope
Before searching:
- What is the primary question?
- What sub-questions must be answered to fully address the primary question?
- What is out of scope (to prevent rabbit holes)?
- Estimated number of sources needed: < 5 for quick, 5-15 for standard, 15+ for deep.

### 2. Search in Waves
**Wave 1 — Orientation**: 2-3 broad searches to understand the landscape and identify key themes.
Use `exa-search` skill for these.

**Wave 2 — Depth**: 4-6 targeted searches to get specifics on each sub-question.
Use `firecrawl` MCP to fetch and read key pages in full (not just summaries).

**Wave 3 — Validation**: 2-3 searches to confirm key claims and check for conflicting information.

### 3. Source Evaluation
For each source, assess:
- **Authority**: Is this a recognized expert, organization, or primary source?
- **Recency**: Is this information current? (Technology and markets change fast.)
- **Bias**: Does the source have an incentive to present one perspective? Note it.
- **Corroboration**: Is this claim supported by at least one other independent source?

Discard sources that fail authority or corroboration checks for factual claims.

### 4. Note-Taking Format
Structure notes to help the synthesizer:
```markdown
## [Topic / Sub-question]

**Finding**: [clear statement of the finding]
**Source**: [title, org, URL, date]
**Confidence**: [High — 2+ sources / Medium — 1 source / Low — speculation/estimate]
**Notes**: [any caveats, date limitations, conflicts with other sources]
```

### 5. Coverage Check
Before finishing, verify:
- [ ] Each sub-question from step 1 has at least one finding
- [ ] Key claims have 2+ sources
- [ ] Any conflicting sources noted, not hidden
- [ ] No obvious alternative perspective ignored

## MCP Tools
- `exa` MCP: use for fast, targeted web search with high relevance
- `firecrawl` MCP: use to fetch and read full page content when a summary is insufficient
