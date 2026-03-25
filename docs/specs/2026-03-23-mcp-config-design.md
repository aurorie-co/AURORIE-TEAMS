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

| Server | Package | Auth | Teams |
|--------|---------|------|-------|
| `github` | `@modelcontextprotocol/server-github` | `GITHUB_TOKEN` | backend, frontend, mobile, product, research (5 teams) |
| `exa` | `exa-mcp-server` | `EXA_API_KEY` | market, product, research (3 teams) |

Note: `filesystem` is intentionally excluded — Claude Code agents have native file access via built-in Read/Write/Edit/Glob/Grep tools. Adding the filesystem MCP server would be redundant.

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": { "EXA_API_KEY": "${EXA_API_KEY}" }
    }
  }
}
```

---

## Per-Team MCP Assignments

### market
SEO agent needs to crawl competitor pages (content extraction) and render JS-heavy pages (visual SEO checks and screenshots).

| Server | Package | Why |
|--------|---------|-----|
| `firecrawl` | `firecrawl-mcp` | Content extraction for SEO audits and competitor page analysis |
| `puppeteer` | `@modelcontextprotocol/server-puppeteer` | Render JS-heavy pages, screenshots for visual SEO inspection |

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}" }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
      "env": {}
    }
  }
}
```

### product
`exa` promoted to shared (3 teams). No team-specific MCP needed.

```json
{
  "mcpServers": {}
}
```

### frontend
QA agent needs to run E2E browser tests.

| Server | Package | Why |
|--------|---------|-----|
| `playwright` | `@playwright/mcp` | Browser automation for E2E and visual regression testing |

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"],
      "env": {}
    }
  }
}
```

### backend
Developer and QA agents need direct database access. The `@modelcontextprotocol/server-postgres` package accepts the connection string as a positional CLI argument.

| Server | Package | Why |
|--------|---------|-----|
| `postgres` | `@modelcontextprotocol/server-postgres` | Database operations, schema inspection, query validation |

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${POSTGRES_URL}"],
      "env": {}
    }
  }
}
```

### data
Analyst and pipeline agents need database access for production queries and local analysis.

| Server | Package | Why |
|--------|---------|-----|
| `postgres` | `@modelcontextprotocol/server-postgres` | Production database queries, pipeline validation |
| `sqlite` | `@modelcontextprotocol/server-sqlite` | Local data analysis, lightweight ad-hoc queries |

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${POSTGRES_URL}"],
      "env": {}
    },
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite"],
      "env": {}
    }
  }
}
```

### research
Web agent uses firecrawl for crawling and exa (now in shared) for neural search.

| Server | Package | Why |
|--------|---------|-----|
| `firecrawl` | `firecrawl-mcp` | Web crawling and content extraction |

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}" }
    }
  }
}
```

### mobile
No team-specific MCP needed. `github` via shared covers devops and code review workflows.

### support
No MCP needed. Ticket content is provided via `input_context` — no external tool access required.

---

## Environment Variables

| Variable | Used by | How injected |
|----------|---------|-------------|
| `GITHUB_TOKEN` | shared — all teams | `env` block in MCP config |
| `EXA_API_KEY` | shared — market, product, research | `env` block in MCP config |
| `FIRECRAWL_API_KEY` | market, research | `env` block in MCP config |
| `POSTGRES_URL` | backend, data | positional CLI arg (not env block) |

`playwright`, `puppeteer`, and `sqlite` require no API keys and run locally.

**Runtime note for `puppeteer`:** Requires Chrome or Chromium to be installed on the host machine. On Linux CI environments, install with `apt-get install -y chromium-browser` or equivalent. On macOS, Chrome must be present at the standard install path or `PUPPETEER_EXECUTABLE_PATH` must be set.

---

## What Does Not Change

- `install.sh` merge logic — no changes needed; already handles per-team mcp.json correctly
- Agent definitions — MCP availability is transparent to agents; they invoke tools naturally
- `.claude/settings.json` in the repo — generated at install time, not committed

---

## Out of Scope

Team-specific SaaS integrations (Jira, Slack, Linear, Salesforce) are intentionally excluded. Teams can add these to their local `.claude/settings.json` after install without modifying the repo.
