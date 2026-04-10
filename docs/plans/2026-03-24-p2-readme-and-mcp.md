# P2 — README Polish + MCP Key Deduplication Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make README a compelling open-source homepage (60-second demo, decision diagram, troubleshooting, security section). Eliminate MCP key collisions by moving shared servers to `shared/mcp.json` and removing duplicate definitions from team files.

**Architecture:** README changes are pure markdown. MCP deduplication moves `postgres` from `teams/backend/mcp.json` and `teams/data/mcp.json` into `shared/mcp.json`; moves `firecrawl` from `teams/market/mcp.json` and `teams/research/mcp.json` into `shared/mcp.json`. The install script logic is unchanged — it processes shared first, so all teams get these servers, which matches current behavior (last definition wins → same config wins). The collision warning test is updated to expect no collision.

**Tech Stack:** markdown, JSON, bash

**Dependency:** P1 lint test should pass before this ships (lint validates mcp.json presence per team).

---

## File Map

| File | Action | What changes |
|------|--------|-------------|
| `shared/mcp.json` | Modify | Add `postgres`, `firecrawl` server definitions |
| `teams/backend/mcp.json` | Modify | Remove `postgres` (now in shared) |
| `teams/data/mcp.json` | Modify | Remove `postgres` (now in shared); keep `sqlite` |
| `teams/market/mcp.json` | Modify | Remove `firecrawl` (now in shared); keep `puppeteer` |
| `teams/research/mcp.json` | Modify | Remove `firecrawl` (now in shared) — file becomes `{"mcpServers": {}}` |
| `tests/install.test.sh` | Modify | Update collision warning test to assert no collision |
| `README.md` | Modify | Add 60-second demo, decision diagram, troubleshooting, security sections |
| `README.zh.md` | Modify | Mirror all new sections in Chinese |

---

### Task 1: Deduplicate MCP keys

**Files:**
- Modify: `shared/mcp.json`
- Modify: `teams/backend/mcp.json`
- Modify: `teams/data/mcp.json`
- Modify: `teams/market/mcp.json`
- Modify: `teams/research/mcp.json`

- [ ] **Step 1: Update `shared/mcp.json`**

  Add `postgres` and `firecrawl` to the shared file. Final content:

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
      },
      "postgres": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "${POSTGRES_URL}"],
        "env": {}
      },
      "firecrawl": {
        "command": "npx",
        "args": ["-y", "firecrawl-mcp"],
        "env": { "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}" }
      }
    }
  }
  ```

- [ ] **Step 2: Update `teams/backend/mcp.json`**

  Remove `postgres` — it's now in shared. Final content:

  ```json
  {
    "mcpServers": {}
  }
  ```

- [ ] **Step 3: Update `teams/data/mcp.json`**

  Remove `postgres`; keep `sqlite`. Final content:

  ```json
  {
    "mcpServers": {
      "sqlite": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite"],
        "env": {}
      }
    }
  }
  ```

- [ ] **Step 4: Update `teams/market/mcp.json`**

  Remove `firecrawl`; keep `puppeteer`. Final content:

  ```json
  {
    "mcpServers": {
      "puppeteer": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "env": {}
      }
    }
  }
  ```

- [ ] **Step 5: Update `teams/research/mcp.json`**

  Remove `firecrawl` — now in shared. Final content:

  ```json
  {
    "mcpServers": {}
  }
  ```

- [ ] **Step 6: Validate all JSON**

  ```bash
  for f in shared/mcp.json teams/backend/mcp.json teams/data/mcp.json teams/market/mcp.json teams/research/mcp.json; do
    jq . $f > /dev/null && echo "✓ $f"
  done
  ```
  Expected: 5 `✓` lines.

- [ ] **Step 7: Run a test install and verify no collision warnings**

  ```bash
  bash tests/install.test.sh 2>&1 | grep -i "collision" || echo "no collisions"
  ```
  Expected: `no collisions`

- [ ] **Step 8: Commit**

  ```bash
  git add shared/mcp.json teams/backend/mcp.json teams/data/mcp.json teams/market/mcp.json teams/research/mcp.json
  git commit -m "fix(mcp): move postgres and firecrawl to shared/mcp.json, eliminate key collisions"
  ```

---

### Task 2: Update install test — remove collision warning assertion

**Files:**
- Modify: `tests/install.test.sh`

- [ ] **Step 1: Find the collision test**

  Locate the block:
  ```bash
  echo ""
  echo "=== Test: postgres key collision warning emitted ==="
  collision_output="$("$REPO_ROOT/install.sh" 2>&1)"
  assert_eq "install warns on postgres key collision" "true" \
    "$([[ "$collision_output" == *"postgres"* ]] && echo true || echo false)"
  ```

- [ ] **Step 2: Replace with a no-collision assertion**

  ```bash
  echo ""
  echo "=== Test: no MCP key collision warnings on clean install ==="
  collision_output="$("$REPO_ROOT/install.sh" 2>&1)"
  assert_eq "install emits no MCP key collision warnings" "false" \
    "$([[ "$collision_output" == *"collision"* ]] && echo true || echo false)"
  ```

- [ ] **Step 3: Run full install tests**

  ```bash
  bash tests/install.test.sh
  ```
  Expected: `Failed: 0`

- [ ] **Step 4: Commit**

  ```bash
  git add tests/install.test.sh
  git commit -m "test: update collision assertion — expect no warnings after mcp deduplication"
  ```

---

### Task 3: Add 60-second demo section to README

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`

- [ ] **Step 1: Add "Demo" section to README.md**

  Insert directly after the "Quick Start" section:

  ```markdown
  ## Demo

  Here's what happens when you run a real task end-to-end.

  **Input** (in Claude Code):
  ```
  @aurorie-orchestrator Write a landing page for our new mobile SDK.
  Audience: iOS and Android developers. Goal: trial signups.
  ```

  **What the orchestrator does:**
  1. Reads `routing.json` — "mobile SDK", "landing page" → market team
  2. Generates a `task-id` and writes `.claude/workspace/tasks/<task-id>.json`
  3. Dispatches `aurorie-market-lead`

  **What the market team does:**
  1. `aurorie-market-seo` researches keywords, writes `seo-report.md`
  2. `aurorie-market-content` drafts the landing page using the SEO report, writes `content.md`
  3. Lead writes `summary.md`

  **Output directory:**
  ```
  .claude/workspace/artifacts/market/<task-id>/
  ├── seo-report.md      ← keyword research, competitor gap analysis
  ├── content.md         ← full landing page copy with H1/H2/CTAs
  └── summary.md         ← what was produced, what to do next
  ```

  **`summary.md` looks like:**
  ```
  Produced a landing page for the mobile SDK targeting iOS/Android developers.
  Primary keyword: "mobile SDK for developers" (volume: high, difficulty: medium).
  Content is at artifacts/market/<task-id>/content.md.
  Recommended next step: run A/B test on the hero CTA copy.
  ```
  ```

- [ ] **Step 2: Mirror in README.zh.md**

  Chinese equivalent:

  ```markdown
  ## 演示

  以下是一次完整的端到端任务执行过程。

  **输入**（在 Claude Code 中）：
  ```
  @aurorie-orchestrator 为我们的移动端 SDK 写一个落地页。
  目标受众：iOS 和 Android 开发者。目标：试用注册。
  ```

  **orchestrator 的执行步骤：**
  1. 读取 `routing.json` — "移动端 SDK"、"落地页" → market 团队
  2. 生成 `task-id`，写入 `.claude/workspace/tasks/<task-id>.json`
  3. 派发 `aurorie-market-lead`

  **market 团队的执行步骤：**
  1. `aurorie-market-seo` 调研关键词，写 `seo-report.md`
  2. `aurorie-market-content` 基于 SEO 报告起草落地页，写 `content.md`
  3. Lead 写 `summary.md`

  **输出目录：**
  ```
  .claude/workspace/artifacts/market/<task-id>/
  ├── seo-report.md      ← 关键词研究、竞品差距分析
  ├── content.md         ← 含 H1/H2/CTA 的完整落地页文案
  └── summary.md         ← 产出说明与建议后续步骤
  ```

  **`summary.md` 示例：**
  ```
  为面向 iOS/Android 开发者的移动端 SDK 制作了落地页。
  核心关键词："mobile SDK for developers"（搜索量：高，难度：中）。
  内容文件：artifacts/market/<task-id>/content.md。
  建议下一步：对 hero CTA 文案进行 A/B 测试。
  ```
  ```

- [ ] **Step 3: Commit**

  ```bash
  git add README.md README.zh.md
  git commit -m "docs: add end-to-end demo section to README"
  ```

---

### Task 4: Add "Which team?" decision guide to README

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`

- [ ] **Step 1: Add Mermaid decision flowchart to README.md**

  Insert after the "Demo" section:

  ````markdown
  ## Which Team?

  Quick reference for routing decisions:

  ```mermaid
  flowchart TD
      A[Your request] --> B{Is it about writing\nor editing content?}
      B -- "Yes, marketing copy\nor SEO" --> MKT[market team]
      B -- "Yes, product spec\nor UX brief" --> PRD[product team]
      B -- No --> C{Is it about\nbuilding software?}
      C -- "Web UI / React / CSS" --> FE[frontend team]
      C -- "API / DB / auth" --> BE[backend team]
      C -- "iOS / Android" --> MOB[mobile team]
      C -- "Terraform / cloud infra" --> INFRA[infra team]
      C -- No --> D{Is it about\ndata or research?}
      D -- "Dashboards / ETL / metrics" --> DATA[data team]
      D -- "Competitor / market research" --> RES[research team]
      D -- "Design system / brand" --> DES[design team]
      D -- "Customer ticket / support" --> SUP[support team]
  ```

  Not sure? Use `@aurorie-orchestrator` — it reads `routing.json` and routes automatically.
  ````

- [ ] **Step 2: Mirror in README.zh.md**

  Chinese version (same diagram, Chinese text):

  ````markdown
  ## 选择哪个团队？

  路由决策快速参考：

  ```mermaid
  flowchart TD
      A[你的请求] --> B{是否关于内容\n写作或编辑？}
      B -- "是：营销文案或 SEO" --> MKT[market 团队]
      B -- "是：产品需求或 UX 说明" --> PRD[product 团队]
      B -- 否 --> C{是否关于\n软件开发？}
      C -- "Web UI / React / CSS" --> FE[frontend 团队]
      C -- "API / 数据库 / 认证" --> BE[backend 团队]
      C -- "iOS / Android" --> MOB[mobile 团队]
      C -- "Terraform / 云基础设施" --> INFRA[infra 团队]
      C -- 否 --> D{是否关于\n数据或调研？}
      D -- "看板 / ETL / 指标" --> DATA[data 团队]
      D -- "竞品 / 市场调研" --> RES[research 团队]
      D -- "设计系统 / 品牌规范" --> DES[design 团队]
      D -- "客户工单 / 支持" --> SUP[support 团队]
  ```

  不确定用哪个团队？使用 `@aurorie-orchestrator` — 它会自动读取 `routing.json` 并路由。
  ````

- [ ] **Step 3: Commit**

  ```bash
  git add README.md README.zh.md
  git commit -m "docs: add which-team decision flowchart to README"
  ```

---

### Task 5: Add Troubleshooting section to README

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`

- [ ] **Step 1: Add Troubleshooting to README.md**

  Insert before the final "Customizing" section:

  ```markdown
  ## Troubleshooting

  **`jq: command not found`**
  Install jq: `brew install jq` (macOS) or `sudo apt install jq` (Linux/Ubuntu).

  **Orchestrator routes to the wrong team**
  Edit `.claude/routing.json` — add specific keywords to the correct team's `positive_keywords`
  and to other teams' `negative_keywords`. Run `bash tests/lint.test.sh` to validate.

  **Multiple teams matched — parallel dispatch is not what I wanted**
  Make your request more specific, or invoke the team lead directly:
  `@aurorie-backend-lead Fix the authentication bug` instead of `@aurorie-orchestrator Fix the bug`.

  **MCP server not available after install**
  Check that the required env var is set before starting Claude Code:
  ```bash
  echo $GITHUB_TOKEN   # should print your token
  echo $POSTGRES_URL   # should print postgresql://...
  ```
  Restart Claude Code after setting env vars.

  **Local workflow override got wiped on upgrade**
  If you ran `install.sh --force-workflows --yes`, your local changes were intentionally
  overwritten. Restore from git: `git checkout .claude/workflows/<team>.md`.
  For future upgrades, omit `--force-workflows` to preserve local changes.

  **Agent file is stale after a team restructure**
  Run `install.sh --detect-orphans` to list agent/skill files that are no longer
  in the upstream repo. Review and delete manually.
  ```

- [ ] **Step 2: Mirror in README.zh.md**

  ```markdown
  ## 常见问题

  **`jq: command not found`**
  安装 jq：`brew install jq`（macOS）或 `sudo apt install jq`（Linux/Ubuntu）。

  **orchestrator 路由到了错误的团队**
  编辑 `.claude/routing.json` — 在正确团队的 `positive_keywords` 中添加关键词，
  在其他团队的 `negative_keywords` 中添加排除词。运行 `bash tests/lint.test.sh` 验证。

  **命中了多个团队，不想要并行派发**
  把请求写得更具体，或直接调用对应团队 Lead：
  `@aurorie-backend-lead 修复认证 bug`，而不是 `@aurorie-orchestrator 修复 bug`。

  **安装后 MCP 服务器不可用**
  确认启动 Claude Code 前已设置所需环境变量：
  ```bash
  echo $GITHUB_TOKEN   # 应输出你的 token
  echo $POSTGRES_URL   # 应输出 postgresql://...
  ```
  设置完环境变量后重启 Claude Code。

  **升级后本地 workflow 覆盖丢失了**
  若运行了 `install.sh --force-workflows --yes`，本地改动已被有意覆盖。
  从 git 恢复：`git checkout .claude/workflows/<team>.md`。
  后续升级时不加 `--force-workflows` 即可保留本地修改。

  **团队重构后 agent 文件过时**
  运行 `install.sh --detect-orphans` 列出不再存在于上游仓库的 agent/skill 文件，
  手动核查后删除。
  ```

- [ ] **Step 3: Commit**

  ```bash
  git add README.md README.zh.md
  git commit -m "docs: add troubleshooting section to README"
  ```

---

### Task 6: Add Security & Permissions section to README

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`

- [ ] **Step 1: Add Security section to README.md**

  Insert after the "Environment Variables" section:

  ```markdown
  ## Security & Permissions

  **GitHub Token scopes**
  The `github` MCP server needs read access to repositories your agents will reference.
  Minimum scopes: `repo:read` (for private repos) or no scopes (public repos only).
  Do not grant `admin`, `delete`, or `write` scopes unless your workflow explicitly needs them.

  **PostgreSQL connection**
  Connect with a read-only user for `data` team tasks (analytics, dashboards).
  Only use a read-write account for `backend` team tasks that run migrations.
  Never point `POSTGRES_URL` at a production database for exploratory analysis.

  **`--yes` flag**
  `install.sh --yes` skips all confirmation prompts. Safe for CI pipelines where
  the target directory is a fresh clone. Do not use on a project directory with
  manually customized workflows unless you also pass `--force-workflows` intentionally.

  **Workspace directory**
  `.claude/workspace/` is gitignored by design — it may contain intermediate
  data, API responses, or draft content from agent runs. Do not commit it.
  ```

- [ ] **Step 2: Mirror in README.zh.md**

  ```markdown
  ## 安全与权限建议

  **GitHub Token 权限范围**
  `github` MCP 服务器需要对 agent 将引用的仓库具有读取权限。
  最小权限范围：`repo:read`（私有仓库）或无 scope（仅公开仓库）。
  除非工作流明确需要，否则不要授予 `admin`、`delete` 或 `write` scope。

  **PostgreSQL 连接**
  `data` 团队任务（分析、看板）请使用只读账户连接。
  只有 `backend` 团队执行 migration 时才需要读写账户。
  不要将生产数据库的 `POSTGRES_URL` 用于探索性分析任务。

  **`--yes` 参数**
  `install.sh --yes` 跳过所有确认提示，适合 CI 流水线中的全新克隆目录。
  如果目标目录已有手动定制的 workflow，不要在没有 `--force-workflows` 的情况下使用。

  **工作区目录**
  `.claude/workspace/` 出于设计原因已加入 .gitignore — 它可能包含 agent 运行产生的
  中间数据、API 响应或草稿内容。不要将其提交到版本控制。
  ```

- [ ] **Step 3: Commit**

  ```bash
  git add README.md README.zh.md
  git commit -m "docs: add security and permissions guidance to README"
  ```

---

### Task 7: Final verification and push

- [ ] **Step 1: Run full test suite**

  ```bash
  bash tests/install.test.sh && bash tests/lint.test.sh
  ```
  Expected: both end with `Failed: 0`

- [ ] **Step 2: Verify MCP table in README still matches reality**

  The README MCP table lists `firecrawl` as "market, research" and `postgres` as "backend, data".
  After this change, all teams technically have both (via shared). Update the MCP table description:

  In README.md, update the `postgres` and `firecrawl` rows:

  ```markdown
  | `postgres` | `@modelcontextprotocol/server-postgres` | All teams (shared) — used by backend, data |
  | `firecrawl` | `firecrawl-mcp` | All teams (shared) — used by market, research |
  ```

  Mirror in README.zh.md.

- [ ] **Step 3: Commit and push**

  ```bash
  git add README.md README.zh.md
  git commit -m "docs: update MCP table to reflect shared postgres and firecrawl"
  git push origin main
  ```
