# MCP Configuration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Populate all team `mcp.json` files and `shared/mcp.json` according to the minimal-principle MCP design spec.

**Architecture:** Each team declares only the MCP servers it genuinely needs; servers used by 3+ teams live in `shared/mcp.json`. `install.sh` already merges all `mcp.json` files into `.claude/settings.json` — no changes to install logic required. Tests use the existing bash test harness: run `install.sh` in a temp dir, then assert specific MCP keys exist in the merged `settings.json`.

**Tech Stack:** JSON, bash, `jq`

---

## File Structure

| File | Action | What changes |
|------|--------|-------------|
| `shared/mcp.json` | Modify | Add `github` + `exa` (both ≥3 teams) |
| `teams/research/mcp.json` | Modify | Remove `exa` (moved to shared); keep `firecrawl` |
| `teams/market/mcp.json` | Modify | Add `firecrawl` + `puppeteer` |
| `teams/frontend/mcp.json` | Modify | Add `playwright` |
| `teams/backend/mcp.json` | Modify | Add `postgres` |
| `teams/data/mcp.json` | Modify | Add `postgres` + `sqlite` |
| `tests/install.test.sh` | Modify | Add per-server key assertions for all new MCP entries |

No changes needed to: `teams/product/mcp.json`, `teams/mobile/mcp.json`, `teams/support/mcp.json` (correctly empty per spec).

---

## Task 1: Shared MCP — github + exa

**Files:**
- Modify: `shared/mcp.json`
- Modify: `teams/research/mcp.json` (remove exa, now in shared)
- Test: `tests/install.test.sh`

- [ ] **Step 1: Write failing tests for github and exa in merged settings.json**

Add to `tests/install.test.sh` inside the `=== Test: default install ===` block, after existing assertions:

```bash
assert_file_contains "github MCP in settings.json"  ".claude/settings.json" '"github"'
assert_file_contains "exa MCP in settings.json"     ".claude/settings.json" '"exa"'
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
bash tests/install.test.sh 2>&1 | tail -10
```

Expected: `✗ github MCP in settings.json` and `✗ exa MCP in settings.json`

- [ ] **Step 3: Update shared/mcp.json**

Replace the contents of `shared/mcp.json` with:

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

- [ ] **Step 4: Update teams/research/mcp.json — remove exa, keep firecrawl**

Replace the contents of `teams/research/mcp.json` with:

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

- [ ] **Step 5: Run tests to verify they pass**

```bash
bash tests/install.test.sh 2>&1 | tail -10
```

Expected: `✓ github MCP in settings.json`, `✓ exa MCP in settings.json`, all prior tests still pass

- [ ] **Step 6: Commit**

```bash
git add shared/mcp.json teams/research/mcp.json tests/install.test.sh
git commit -m "feat(mcp): add github+exa to shared, move exa out of research"
```

---

## Task 2: Market + Frontend MCP

**Files:**
- Modify: `teams/market/mcp.json`
- Modify: `teams/frontend/mcp.json`
- Test: `tests/install.test.sh`

- [ ] **Step 1: Write failing tests for firecrawl, puppeteer, playwright**

Add to `tests/install.test.sh` inside the `=== Test: default install ===` block:

```bash
assert_file_contains "firecrawl MCP in settings.json"  ".claude/settings.json" '"firecrawl"'
assert_file_contains "puppeteer MCP in settings.json"  ".claude/settings.json" '"puppeteer"'
assert_file_contains "playwright MCP in settings.json" ".claude/settings.json" '"playwright"'
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
bash tests/install.test.sh 2>&1 | tail -10
```

Expected: `✗ firecrawl MCP in settings.json`, `✗ puppeteer MCP in settings.json`, `✗ playwright MCP in settings.json`

Note: `firecrawl` test may already pass if Task 1 is done and research/mcp.json has it — that is correct behaviour.

- [ ] **Step 3: Update teams/market/mcp.json**

Replace the contents of `teams/market/mcp.json` with:

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

- [ ] **Step 4: Update teams/frontend/mcp.json**

Replace the contents of `teams/frontend/mcp.json` with:

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

- [ ] **Step 5: Run tests to verify they pass**

```bash
bash tests/install.test.sh 2>&1 | tail -10
```

Expected: `✓ firecrawl MCP in settings.json`, `✓ puppeteer MCP in settings.json`, `✓ playwright MCP in settings.json`

- [ ] **Step 6: Commit**

```bash
git add teams/market/mcp.json teams/frontend/mcp.json tests/install.test.sh
git commit -m "feat(mcp): add firecrawl+puppeteer to market, playwright to frontend"
```

---

## Task 3: Backend + Data MCP

**Files:**
- Modify: `teams/backend/mcp.json`
- Modify: `teams/data/mcp.json`
- Test: `tests/install.test.sh`

- [ ] **Step 1: Write failing tests for postgres and sqlite**

Add to `tests/install.test.sh` inside the `=== Test: default install ===` block:

```bash
assert_file_contains "postgres MCP in settings.json" ".claude/settings.json" '"postgres"'
assert_file_contains "sqlite MCP in settings.json"   ".claude/settings.json" '"sqlite"'
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
bash tests/install.test.sh 2>&1 | tail -10
```

Expected: `✗ postgres MCP in settings.json`, `✗ sqlite MCP in settings.json`

- [ ] **Step 3: Update teams/backend/mcp.json**

Replace the contents of `teams/backend/mcp.json` with:

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

- [ ] **Step 4: Update teams/data/mcp.json**

Replace the contents of `teams/data/mcp.json` with:

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

- [ ] **Step 5: Run all tests to verify full suite passes**

```bash
bash tests/install.test.sh 2>&1
```

Expected output ends with:
```
=== Results ===
  Passed: 31
  Failed: 0
```

(23 existing + 8 new assertions: github, exa, firecrawl, puppeteer, playwright, postgres, sqlite, collision-warning)

- [ ] **Step 6: Commit**

```bash
git add teams/backend/mcp.json teams/data/mcp.json tests/install.test.sh
git commit -m "feat(mcp): add postgres to backend, postgres+sqlite to data"
```

---

## Task 4: Collision-detection test + README env vars update

**Files:**
- Modify: `tests/install.test.sh`
- Modify: `README.md`
- Modify: `README.zh.md`

- [ ] **Step 1: Write a test that verifies postgres key collision warning is emitted**

Both backend and data declare `postgres`. The install.sh collision detection should warn. Add after existing tests in `tests/install.test.sh`:

```bash
echo ""
echo "=== Test: postgres key collision warning emitted ==="
collision_output="$("$REPO_ROOT/install.sh" 2>&1)"
assert_eq "install warns on postgres key collision" "true" \
  "$([[ "$collision_output" == *"postgres"* ]] && echo true || echo false)"
```

- [ ] **Step 2: Verify the test already passes (no red-first step needed)**

By the time Task 4 runs, both `teams/backend/mcp.json` and `teams/data/mcp.json` already declare `postgres` (added in Task 3). The collision warning is already being emitted by `install.sh`. There is no red-first step here — the precondition is already met.

```bash
bash tests/install.test.sh 2>&1 | grep "collision warning"
```

Expected: `✓ install warns on postgres key collision`

- [ ] **Step 3: Run full test suite to confirm**

```bash
bash tests/install.test.sh 2>&1
```

Expected: all tests pass including the collision warning test.

- [ ] **Step 4: Update README.md Environment Variables section**

Replace the current env vars block in `README.md`:

```bash
export GITHUB_TOKEN=...        # GitHub API access (research, frontend, backend teams)
export EXA_API_KEY=...         # Exa neural search (research, market teams)
export FIRECRAWL_API_KEY=...   # Web crawling (research, market teams)
```

With:

```bash
export GITHUB_TOKEN=...        # GitHub API — all teams via shared MCP
export EXA_API_KEY=...         # Exa neural search — market, product, research teams
export FIRECRAWL_API_KEY=...   # Web crawling — market, research teams
export POSTGRES_URL=...        # PostgreSQL connection string — backend, data teams
                               # Format: postgresql://user:password@host:5432/dbname
```

- [ ] **Step 5: Update README.zh.md Environment Variables section**

Replace the current env vars block in `README.zh.md`:

```bash
export GITHUB_TOKEN=...        # GitHub API（research、frontend、backend 团队使用）
export EXA_API_KEY=...         # Exa 神经搜索（research、market 团队使用）
export FIRECRAWL_API_KEY=...   # Web 爬取（research、market 团队使用）
```

With:

```bash
export GITHUB_TOKEN=...        # GitHub API — 所有团队通过 shared MCP 使用
export EXA_API_KEY=...         # Exa 神经搜索 — market、product、research 团队
export FIRECRAWL_API_KEY=...   # Web 爬取 — market、research 团队
export POSTGRES_URL=...        # PostgreSQL 连接串 — backend、data 团队
                               # 格式：postgresql://user:password@host:5432/dbname
```

- [ ] **Step 6: Run full test suite one final time**

```bash
bash tests/install.test.sh 2>&1
```

Expected: all tests pass, no failures.

- [ ] **Step 7: Commit**

```bash
git add tests/install.test.sh README.md README.zh.md
git commit -m "feat(mcp): add collision test, update README env vars"
```

---

## Verification

After all 4 tasks are complete, verify the final merged output:

```bash
# Run a fresh install in a temp dir and inspect the result
VERIFY_DIR=$(mktemp -d)
cd $VERIFY_DIR && touch .gitignore
/path/to/aurorie-teams/install.sh > /dev/null
jq '.mcpServers | keys' .claude/settings.json
```

Expected keys in settings.json:
```json
["exa", "firecrawl", "github", "playwright", "postgres", "puppeteer", "sqlite"]
```

`filesystem` must NOT appear (excluded per spec).
