# MCP Configuration Design

## Goal

Define which MCP servers each team needs, following a minimal principle: only add a server when its absence prevents an agent from doing its core job. Configuration is a generic template — any company installing aurorie-teams can activate servers via environment variables.

## Architecture

**Tiered placement rule:**
- **`shared/mcp.json`** — servers used by 3 or more teams
- **`teams/<team>/mcp.json`** — servers specific to 1–2 teams
- `install.sh` merges all files into `.claude/settings.json` at install time (collision detection already implemented)

---

## shared/mcp.json

Used by 5 teams (backend, frontend, mobile, product, research).

| Server | Package | Auth |
|--------|---------|------|
| `github` | `@modelcontextprotocol/server-github` | `GITHUB_TOKEN` |
| `filesystem` | `@modelcontextprotocol/server-filesystem` | none |

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {}
    }
  }
}
```

---

## Per-Team MCP Assignments

### market
SEO agent needs to crawl competitor pages (content extraction) and render JS-heavy pages (visual SEO checks).

| Server | Package | Why |
|--------|---------|-----|
| `firecrawl` | `firecrawl-mcp` | Content extraction for SEO audits and competitor page analysis |
| `puppeteer` | `@modelcontextprotocol/server-puppeteer` | Render JS-heavy pages, screenshots for visual SEO inspection |

### product
Researcher agent needs neural search for competitive and market research.

| Server | Package | Why |
|--------|---------|-----|
| `exa` | `exa-mcp-server` | Neural search for competitor product research and market analysis |

### frontend
QA agent needs to run E2E browser tests.

| Server | Package | Why |
|--------|---------|-----|
| `playwright` | `@playwright/mcp` | Browser automation for E2E and visual regression testing |

### backend
Developer and QA agents need direct database access.

| Server | Package | Why |
|--------|---------|-----|
| `postgres` | `@modelcontextprotocol/server-postgres` | Database operations, schema inspection, query validation |

### data
Analyst and pipeline agents need database access for production queries and local analysis.

| Server | Package | Why |
|--------|---------|-----|
| `postgres` | `@modelcontextprotocol/server-postgres` | Production database queries, pipeline validation |
| `sqlite` | `@modelcontextprotocol/server-sqlite` | Local data analysis, lightweight ad-hoc queries |

### research
Web agent needs web search and crawling. Puppeteer added as fallback for JS-rendered pages firecrawl cannot access.

| Server | Package | Why |
|--------|---------|-----|
| `firecrawl` | `firecrawl-mcp` | Web crawling and content extraction (existing) |
| `exa` | `exa-mcp-server` | Neural search for research queries (existing) |
| `puppeteer` | `@modelcontextprotocol/server-puppeteer` | Fallback for JS-rendered pages firecrawl cannot reach |

### mobile
No team-specific MCP needed. `github` via shared covers devops and code review workflows.

### support
No MCP needed. Ticket content is provided via `input_context` — no external tool access required.

---

## Environment Variables

| Variable | Used by | Required |
|----------|---------|---------|
| `GITHUB_TOKEN` | shared (all teams) | Yes, for GitHub MCP |
| `FIRECRAWL_API_KEY` | market, research | Yes, for firecrawl |
| `EXA_API_KEY` | product, research | Yes, for exa |
| `POSTGRES_URL` | backend, data | Yes, for postgres |

`playwright`, `puppeteer`, and `sqlite` require no API keys — they run locally.

---

## What Does Not Change

- `install.sh` merge logic — no changes needed, already handles per-team mcp.json correctly
- `.claude/settings.json` in the repo — this file is generated at install time, not committed
- Agent definitions — MCP availability is transparent to agents; they use tools naturally

---

## Out of Scope

Team-specific SaaS integrations (Jira, Slack, Linear, Salesforce) are intentionally excluded. Teams can add these to their local `.claude/settings.json` after install without modifying the repo.
