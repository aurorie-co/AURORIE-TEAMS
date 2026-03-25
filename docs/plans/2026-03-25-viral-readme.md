# Viral README Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully rewrite `README.md` and `README.zh.md` from engineering config doc to "AI Company OS" product narrative that hooks, activates, and retains users.

**Architecture:** Two files rewritten sequentially. README.md is the source of truth written in three commits (Sections 1–4, 5–8, 9–12). README.zh.md is a full Chinese translation written in a single commit, with verbatim code blocks and diagrams. Write both files using the Write tool — do not use bash heredocs, as nested fenced code blocks will break.

**Tech Stack:** Markdown, Mermaid, GitHub Flavored Markdown badges

---

## File Map

| File | Action | What changes |
|------|--------|-------------|
| `README.md` | Full rewrite | All 393 lines replaced with 13-section viral structure |
| `README.zh.md` | Full rewrite | Synchronized ZH translation of README.md |

---

### Task 1: Write README.md Sections 1–4 (Hook → Positioning)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read the current README.md**

  Read `README.md` and note the badge URLs on lines 3–6 (they will be reused verbatim).

- [ ] **Step 2: Write README.md Sections 1–4 using the Write tool**

  Write the following as the complete new `README.md` (this replaces the full existing file).
  Use the Write tool — do NOT use a bash heredoc, as the file contains fenced code blocks.

  File content:

  ---
  START OF README.md CONTENT
  ---

  # AURORIE TEAMS

  > Turn Claude Code into a fully-operational AI startup team in 60 seconds — with real artifacts.

  ⚡ 34 Agents · 10 Teams · 1 Orchestrator
  ⚡ Plug-and-play AI workflows for real-world execution
  ⚡ Built for builders, founders, and power users

  ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue?style=flat-square)
  ![Agents](https://img.shields.io/badge/agents-34-informational?style=flat-square)
  ![Teams](https://img.shields.io/badge/teams-10-informational?style=flat-square)
  ![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

  **Languages:** English | [中文](README.zh.md)

  ---

  ## Install in 60 seconds

  ```bash
  git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
  cd /path/to/your-project
  /tmp/aurorie-teams/install.sh
  ```

  Then just ask:

  ```
  @orchestrator "Build me a SaaS product from scratch"
  ```

  _(or simply: "Build me a SaaS product from scratch" — the system routes automatically)_

  ---

  ## 🎬 What it actually does

  ### Input

  ```
  @orchestrator "Build a crypto trading dashboard with real-time data and mobile support"
  ```

  ### What happens internally

  1. Orchestrator analyzes intent
  2. Selects relevant teams:
     - Product Team  (requirements)
     - Backend Team  (API design)
     - Frontend Team (UI)
     - Mobile Team   (app structure)
  3. Each team executes its workflow
  4. Outputs are written to structured artifacts

  ### Output

  ```
  .claude/workspace/
  ├── tasks/
  │   └── task-001.json
  └── artifacts/
      ├── product/prd.md
      ├── backend/api-design.md
      ├── frontend/ui-spec.md
      └── mobile/app-architecture.md
  ```

  💡 You just went from idea → structured execution plan in seconds.

  Each file is a reusable artifact — not just a response.

  ---

  ## 🧩 How it works

  You don't interact with agents directly — the system does it for you:

  ```mermaid
  graph TD
      U([User Request]) --> O[Orchestrator]
      O --> T1[Product Team]
      O --> T2[Backend Team]
      O --> T3[Frontend Team]
      O --> T4[Mobile Team]
      O --> T5[Data Team]
      O --> T6[... 5 more teams]

      style O fill:#1a1a2e,color:#fff,stroke:#4a4a8a
      style U fill:#16213e,color:#fff,stroke:#4a4a8a
  ```

  Three layers:

  1. **Orchestrator** — routes your request to the right teams
  2. **Teams (10 domains)** — each specializes in a function
  3. **Agents (34 total)** — each executes specific tasks with defined workflows

  > ChatGPT → one smart person
  > AURORIE TEAMS → a full company working together

  _Want to see the full system? → See [Architecture](#-architecture) below._

  ---

  ## ⚡ Why not just use ChatGPT?

  Because real work is not single-step.

  | ChatGPT | AURORIE TEAMS |
  |---------|---------------|
  | One response | Multi-step execution |
  | Generalist | Specialized teams |
  | Ephemeral output | Structured artifacts |
  | Manual thinking | Automated orchestration |

  You don't need one answer.
  You need a team that executes.

  Ready to try it? ↓

  ---
  END OF README.md CONTENT (Sections 1–4 only — more sections will be appended in Tasks 2 and 3)
  ---

- [ ] **Step 3: Verify file written correctly**

  ```bash
  head -3 README.md
  grep -c "^## " README.md
  ```
  Expected: first line is `# AURORIE TEAMS`, section count is `4`

- [ ] **Step 4: Commit**

  ```bash
  git add README.md
  git commit -m "docs(readme): add sections 1-4 — hero, demo, mental model, positioning"
  ```

---

### Task 2: Append README.md Sections 5–8 (Credibility → Activation)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read README.md**

  Read the current README.md to get the existing content (needed before Write tool can edit it).

- [ ] **Step 2: Append Sections 5–8 to README.md using the Write tool**

  Rewrite README.md as its full current content PLUS the following appended at the end.
  Use the Write tool. The new content to append:

  ---
  APPEND TO README.md
  ---

  ## 🧠 Intelligent Routing

  Each routing decision is explainable — not a black box.

  Each request is scored against every team rule:
  - **+1** for each `positive_keywords` match
  - **−2** for each `negative_keywords` match (strong disqualifier)
  - `example_requests` break ties

  Example:

  ```
  "Why did revenue drop?"
  → Data     (+score: data, metrics, report)
  → Research (+score: investigate, compare)
  → Backend  (−score: database penalty)
  Final: Data + Research

  "Build a mobile app"
  → Mobile  (+score: iOS, Android, native)
  → Backend (+score: API, server)
  → Frontend (−score: mobile app penalty)
  Final: Mobile + Backend
  ```

  Routing is deterministic at the rule level, and adaptive at the system level.

  You can customize routing in `.claude/routing.json`.

  ---

  ## 🏗 Architecture

  Here's the full system:

  ```mermaid
  graph TD
      U([User Request]) --> O[orchestrator<br/>reads routing.json]
      O --> ML[market-lead]
      O --> PL[product-lead]
      O --> RL[research-lead]
      O --> SL[support-lead]
      O --> FL[frontend-lead]
      O --> BL[backend-lead]
      O --> IL[infra-lead]
      O --> DL[design-lead]
      O --> DAL[data-lead]
      O --> MOL[mobile-lead]

      ML --> MS1[seo]
      ML --> MS2[content]
      ML --> MS3[analytics]

      PL --> PS1[pm]
      PL --> PS2[ux]
      PL --> PS3[researcher]

      FL --> FS1[developer]
      FL --> FS2[qa]
      FL --> FS3[devops]

      MS2 --> A1[(artifact)]
      PS1 --> A2[(artifact)]
      FS1 --> A3[(artifact)]

      style O fill:#1a1a2e,color:#fff,stroke:#4a4a8a
      style U fill:#16213e,color:#fff,stroke:#4a4a8a
  ```

  Each team includes:
  - Agents (specialists with defined roles)
  - Workflows (step-by-step execution guides)
  - Skills (reusable task modules)
  - MCP integrations (tool access per team)

  ---

  ## 🛠 Installation

  Requirements: macOS or Linux (bash 3.2+) · `jq` · `uuidgen` or `python3` · Node.js

  ```bash
  # 1. Clone the library
  git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams

  # 2. Install into your project
  cd /path/to/your-project
  /tmp/aurorie-teams/install.sh

  # 3. Add API keys (optional but recommended)
  export GITHUB_TOKEN=...
  export EXA_API_KEY=...
  export FIRECRAWL_API_KEY=...

  # 4. Verify
  # In Claude Code: @orchestrator "Test the system"
  # You should see routing + task output.
  ```

  Done ✅ Your Claude Code is now an AI startup team.

  ### Install flags

  ```
  --force-workflows   Overwrite existing workflow + routing overrides
  --yes               Skip all confirmation prompts
  --detect-orphans    Report stale agent/skill files no longer in repo
  ```

  ### Upgrade

  ```bash
  git -C /tmp/aurorie-teams pull
  cd /path/to/your-project && /tmp/aurorie-teams/install.sh
  ```

  ---

  ## 🧪 Try these prompts

  Each prompt triggers a different team workflow — try one to see the system in action.

  ### Build a product

  ```
  @orchestrator "Create a SaaS for AI agents marketplace"
  ```

  Triggers:
  - Product Team
  - Backend Team
  - Frontend Team

  Output:
  ```
  .claude/workspace/artifacts/product/prd.md
  .claude/workspace/artifacts/backend/api-design.md
  .claude/workspace/artifacts/frontend/ui-spec.md
  ```

  Copy and run this — you'll get real artifacts.

  ---

  ### Analyze data

  ```
  @orchestrator "Investigate why our DAU dropped 30% last week"
  ```

  Triggers:
  - Data Team
  - Research Team

  Output:
  ```
  .claude/workspace/artifacts/data/analysis.md
  .claude/workspace/artifacts/research/synthesis.md
  ```

  Copy and run this — you'll get real artifacts.

  ---

  ### Build an app

  ```
  @orchestrator "Design a mobile app for habit tracking with iOS and Android support"
  ```

  Triggers:
  - Mobile Team
  - Backend Team
  - Product Team

  Output:
  ```
  .claude/workspace/artifacts/mobile/app-architecture.md
  .claude/workspace/artifacts/backend/api-design.md
  .claude/workspace/artifacts/product/prd.md
  ```

  Copy and run this — you'll get real artifacts.

  ---

  ### Research a market

  ```
  @orchestrator "Compare the top 5 AI code generation tools — pricing, features, positioning"
  ```

  Triggers:
  - Research Team

  Output:
  ```
  .claude/workspace/artifacts/research/competitive-analysis.md
  .claude/workspace/artifacts/research/summary.md
  ```

  Copy and run this — you'll get real artifacts.

  ---
  END OF APPEND
  ---

- [ ] **Step 3: Verify sections appended**

  ```bash
  grep -c "^## " README.md
  ```
  Expected: `8`

- [ ] **Step 4: Commit**

  ```bash
  git add README.md
  git commit -m "docs(readme): add sections 5-8 — routing, architecture, install, try prompts"
  ```

---

### Task 3: Append README.md Sections 9–13 (Power → Tests)

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read README.md**

  Read current README.md (needed before Write tool can edit).

- [ ] **Step 2: Append Sections 9–13 using the Write tool**

  Rewrite README.md as its full current content PLUS the following appended at the end:

  ---
  APPEND TO README.md
  ---

  ## 🔧 Customization

  ### Customize behavior
  Edit `.claude/workflows/<team>.md` to change how a team operates.

  ### Customize intelligence
  Edit `.claude/routing.json` — v2 schema supports `positive_keywords` (+1), `negative_keywords` (−2), and `example_requests` per rule.

  ### Customize tools
  Extend MCP integrations via `.claude/settings.json`.

  ---

  ## ⚠️ Safety

  Use read-only credentials where possible. Review generated artifacts before acting on them.

  ### Details

  - **Agents generate outputs — they do not execute external actions unless you do.**
    Agents write files to `.claude/workspace/artifacts/`. They do not call external APIs,
    run shell commands, or modify your database unless you explicitly wire that up.
  - **Nothing runs without your approval.**
  - Avoid running on production systems during initial setup.
  - Review `.claude/settings.json` to see and control which tools each agent can access.

  ---

  ## 🗺 Roadmap

  We're building the AI company OS.

  **v1.x — Reliable execution**
  - ✓ 10 specialized teams, 34 agents
  - ✓ v2 routing with positive/negative scoring
  - ✓ Lint + install test suites

  **v2.0 — Intelligent systems**
  - [ ] Confidence-based routing
  - [ ] UI dashboard
  - [ ] Visual workflow editor

  **Long-term — AI-native companies**
  - [ ] Agent marketplace
  - [ ] Memory system
  - [ ] Cross-project orchestration

  ---

  ## 🤝 Contributing

  We're building the AI company OS — and we're opinionated about it.

  Want to help?
  - Add new teams
  - Improve routing logic
  - Build workflows
  - Share use cases

  We value coherence over volume.

  Open a PR 🚀

  ---

  ## Tests

  Two test suites live in `tests/`:

  | Script | What it tests |
  |--------|--------------|
  | `tests/install.test.sh` | Full install lifecycle: file placement, routing preservation, MCP merge, orphan detection |
  | `tests/lint.test.sh` | Source tree consistency: agent/workflow/skill/routing contract validation |

  Run both with:

  ```bash
  bash tests/install.test.sh && bash tests/lint.test.sh
  ```

  ---
  END OF APPEND
  ---

- [ ] **Step 3: Verify all 13 sections present**

  ```bash
  grep -c "^## " README.md
  ```
  Expected: `13`

  ```bash
  grep "^## " README.md
  ```
  Expected output (in order):
  ```
  ## Install in 60 seconds
  ## 🎬 What it actually does
  ## 🧩 How it works
  ## ⚡ Why not just use ChatGPT?
  ## 🧠 Intelligent Routing
  ## 🏗 Architecture
  ## 🛠 Installation
  ## 🧪 Try these prompts
  ## 🔧 Customization
  ## ⚠️ Safety
  ## 🗺 Roadmap
  ## 🤝 Contributing
  ## Tests
  ```

- [ ] **Step 4: Spot-check key copy**

  ```bash
  grep "with real artifacts" README.md
  grep "one smart person" README.md
  grep "Nothing runs without your approval" README.md
  grep "deterministic at the rule level" README.md
  grep "Each prompt triggers a different team workflow" README.md
  ```
  Expected: all 5 lines present

- [ ] **Step 5: Run lint tests**

  ```bash
  bash tests/lint.test.sh 2>&1 | tail -4
  ```
  Expected: `Failed: 0`

- [ ] **Step 6: Commit**

  ```bash
  git add README.md
  git commit -m "docs(readme): add sections 9-13 — customization, safety, roadmap, contributing, tests"
  ```

---

### Task 4: Write README.zh.md (synchronized ZH translation)

**Files:**
- Modify: `README.zh.md`

- [ ] **Step 1: Read README.zh.md**

  Read current README.zh.md (needed before Write tool can edit).

- [ ] **Step 2: Write the complete README.zh.md using the Write tool**

  Write the following as the complete new `README.zh.md`.
  Rules: all prose is Chinese; all code blocks, bash commands, file trees, badge URLs, and Mermaid diagrams are verbatim (no translation).

  ---
  START OF README.zh.md CONTENT
  ---

  # AURORIE TEAMS

  > 60 秒内，将 Claude Code 变成一支全功能 AI 创业团队——并产出真实文件。

  ⚡ 34 个 Agent · 10 个团队 · 1 个 Orchestrator
  ⚡ 即插即用的 AI 工作流，面向真实执行场景
  ⚡ 为构建者、创始人和高级用户而生

  ![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue?style=flat-square)
  ![Agents](https://img.shields.io/badge/agents-34-informational?style=flat-square)
  ![Teams](https://img.shields.io/badge/teams-10-informational?style=flat-square)
  ![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

  **语言：** [English](README.md) | 中文

  ---

  ## 60 秒安装

  ```bash
  git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
  cd /path/to/your-project
  /tmp/aurorie-teams/install.sh
  ```

  然后直接说：

  ```
  @orchestrator "Build me a SaaS product from scratch"
  ```

  _（或者直接说："Build me a SaaS product from scratch"——系统会自动路由）_

  ---

  ## 🎬 实际效果

  ### 输入

  ```
  @orchestrator "Build a crypto trading dashboard with real-time data and mobile support"
  ```

  ### 内部流程

  1. Orchestrator 分析意图
  2. 选择相关团队：
     - Product Team（需求）
     - Backend Team（API 设计）
     - Frontend Team（UI）
     - Mobile Team（App 结构）
  3. 每个团队执行其工作流
  4. 输出写入结构化产出文件

  ### 输出

  ```
  .claude/workspace/
  ├── tasks/
  │   └── task-001.json
  └── artifacts/
      ├── product/prd.md
      ├── backend/api-design.md
      ├── frontend/ui-spec.md
      └── mobile/app-architecture.md
  ```

  💡 你刚刚在几秒内完成了从想法到结构化执行计划的全过程。

  每个文件都是可复用的产出物——不只是一段对话回复。

  ---

  ## 🧩 工作原理

  你不需要直接操控 Agent——系统会替你完成这一切：

  ```mermaid
  graph TD
      U([User Request]) --> O[Orchestrator]
      O --> T1[Product Team]
      O --> T2[Backend Team]
      O --> T3[Frontend Team]
      O --> T4[Mobile Team]
      O --> T5[Data Team]
      O --> T6[... 5 more teams]

      style O fill:#1a1a2e,color:#fff,stroke:#4a4a8a
      style U fill:#16213e,color:#fff,stroke:#4a4a8a
  ```

  三层架构：

  1. **Orchestrator** — 将请求路由到正确的团队
  2. **Teams（10 个领域）** — 每个团队专注于一个职能
  3. **Agents（共 34 个）** — 每个 Agent 按定义的工作流执行具体任务

  > ChatGPT → 一个聪明的人
  > AURORIE TEAMS → 一整家公司协同工作

  _想看完整系统架构？→ 查看下方[系统架构](#-系统架构)。_

  ---

  ## ⚡ 为什么不直接用 ChatGPT？

  因为真实工作不是单步的。

  | ChatGPT | AURORIE TEAMS |
  |---------|---------------|
  | 一个回答 | 多步执行 |
  | 通才 | 专业团队 |
  | 临时输出 | 结构化产出文件 |
  | 手动思考 | 自动编排 |

  你不需要一个答案。
  你需要一支能执行的团队。

  准备好试试了吗？↓

  ---

  ## 🧠 智能路由

  每次路由决策都是可解释的——不是黑箱。

  系统对每条团队规则进行打分：
  - **+1**：每个 `positive_keywords` 命中
  - **−2**：每个 `negative_keywords` 命中（强排除信号）
  - 同分时用 `example_requests` 决胜

  示例：

  ```
  "Why did revenue drop?"
  → Data     (+score: data, metrics, report)
  → Research (+score: investigate, compare)
  → Backend  (−score: database penalty)
  Final: Data + Research

  "Build a mobile app"
  → Mobile  (+score: iOS, Android, native)
  → Backend (+score: API, server)
  → Frontend (−score: mobile app penalty)
  Final: Mobile + Backend
  ```

  路由在规则层面是确定性的，在系统层面是自适应的。

  你可以在 `.claude/routing.json` 中自定义路由规则。

  ---

  ## 🏗 系统架构

  完整系统如下：

  ```mermaid
  graph TD
      U([User Request]) --> O[orchestrator<br/>reads routing.json]
      O --> ML[market-lead]
      O --> PL[product-lead]
      O --> RL[research-lead]
      O --> SL[support-lead]
      O --> FL[frontend-lead]
      O --> BL[backend-lead]
      O --> IL[infra-lead]
      O --> DL[design-lead]
      O --> DAL[data-lead]
      O --> MOL[mobile-lead]

      ML --> MS1[seo]
      ML --> MS2[content]
      ML --> MS3[analytics]

      PL --> PS1[pm]
      PL --> PS2[ux]
      PL --> PS3[researcher]

      FL --> FS1[developer]
      FL --> FS2[qa]
      FL --> FS3[devops]

      MS2 --> A1[(artifact)]
      PS1 --> A2[(artifact)]
      FS1 --> A3[(artifact)]

      style O fill:#1a1a2e,color:#fff,stroke:#4a4a8a
      style U fill:#16213e,color:#fff,stroke:#4a4a8a
  ```

  每个团队包含：
  - Agents（具有明确角色的 specialist）
  - Workflows（逐步执行指南）
  - Skills（可复用任务模块）
  - MCP integrations（每个团队的工具访问权限）

  ---

  ## 🛠 安装

  环境要求：macOS 或 Linux（bash 3.2+）· `jq` · `uuidgen` 或 `python3` · Node.js

  ```bash
  # 1. 克隆库
  git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams

  # 2. 安装到你的项目
  cd /path/to/your-project
  /tmp/aurorie-teams/install.sh

  # 3. 添加 API 密钥（可选但推荐）
  export GITHUB_TOKEN=...
  export EXA_API_KEY=...
  export FIRECRAWL_API_KEY=...

  # 4. 验证
  # 在 Claude Code 中：@orchestrator "Test the system"
  # 你应该能看到路由 + 任务输出。
  ```

  完成 ✅ 你的 Claude Code 现在已经是一支 AI 创业团队了。

  ### 安装参数

  ```
  --force-workflows   覆盖本地已修改的 workflow 和 routing 文件
  --yes               跳过所有确认提示
  --detect-orphans    检测已不在仓库中的过时 agent/skill 文件
  ```

  ### 升级

  ```bash
  git -C /tmp/aurorie-teams pull
  cd /path/to/your-project && /tmp/aurorie-teams/install.sh
  ```

  ---

  ## 🧪 试试这些 prompt

  每个 prompt 都会触发不同的团队工作流——试一个，看看系统如何运转。

  ### 构建产品

  ```
  @orchestrator "Create a SaaS for AI agents marketplace"
  ```

  触发团队：
  - Product Team
  - Backend Team
  - Frontend Team

  输出：
  ```
  .claude/workspace/artifacts/product/prd.md
  .claude/workspace/artifacts/backend/api-design.md
  .claude/workspace/artifacts/frontend/ui-spec.md
  ```

  复制并运行——你会得到真实的产出文件。

  ---

  ### 分析数据

  ```
  @orchestrator "Investigate why our DAU dropped 30% last week"
  ```

  触发团队：
  - Data Team
  - Research Team

  输出：
  ```
  .claude/workspace/artifacts/data/analysis.md
  .claude/workspace/artifacts/research/synthesis.md
  ```

  复制并运行——你会得到真实的产出文件。

  ---

  ### 构建 App

  ```
  @orchestrator "Design a mobile app for habit tracking with iOS and Android support"
  ```

  触发团队：
  - Mobile Team
  - Backend Team
  - Product Team

  输出：
  ```
  .claude/workspace/artifacts/mobile/app-architecture.md
  .claude/workspace/artifacts/backend/api-design.md
  .claude/workspace/artifacts/product/prd.md
  ```

  复制并运行——你会得到真实的产出文件。

  ---

  ### 市场调研

  ```
  @orchestrator "Compare the top 5 AI code generation tools — pricing, features, positioning"
  ```

  触发团队：
  - Research Team

  输出：
  ```
  .claude/workspace/artifacts/research/competitive-analysis.md
  .claude/workspace/artifacts/research/summary.md
  ```

  复制并运行——你会得到真实的产出文件。

  ---

  ## 🔧 自定义

  ### 自定义行为
  编辑 `.claude/workflows/<team>.md`，修改团队的运作方式。

  ### 自定义智能
  编辑 `.claude/routing.json`——v2 schema 每条规则支持 `positive_keywords`（+1）、`negative_keywords`（−2）和 `example_requests`。

  ### 自定义工具
  通过 `.claude/settings.json` 扩展 MCP 集成。

  ---

  ## ⚠️ 安全说明

  尽量使用只读凭证。在执行任何操作前，请先审阅生成的产出文件。

  ### 详情

  - **Agent 只生成输出——除非你主动触发，否则不会执行任何外部操作。**
    Agent 将文件写入 `.claude/workspace/artifacts/`。它们不会调用外部 API、
    运行 shell 命令或修改数据库，除非你明确接入这些能力。
  - **没有你的确认，什么都不会执行。**
  - 初始设置阶段，避免在生产系统上运行。
  - 查看 `.claude/settings.json` 了解并控制每个 Agent 的工具访问权限。

  ---

  ## 🗺 路线图

  我们在构建 AI 公司操作系统。

  **v1.x — 可靠执行**
  - ✓ 10 个专业团队，34 个 Agent
  - ✓ 正负分值 v2 路由
  - ✓ Lint + install 测试套件

  **v2.0 — 智能系统**
  - [ ] 置信度路由
  - [ ] UI 控制台
  - [ ] 可视化工作流编辑器

  **长期 — AI 原生公司**
  - [ ] Agent 市场
  - [ ] 记忆系统
  - [ ] 跨项目编排

  ---

  ## 🤝 参与贡献

  我们在构建 AI 公司操作系统——而且我们对此有明确的主张。

  欢迎贡献：
  - 新增团队
  - 优化路由逻辑
  - 构建工作流
  - 分享使用案例

  我们重视一致性，而非数量。

  提交 PR 🚀

  ---

  ## 测试

  `tests/` 目录中有两个测试套件：

  | 脚本 | 测试内容 |
  |--------|--------------|
  | `tests/install.test.sh` | 完整安装生命周期：文件放置、路由保留、MCP 合并、孤立文件检测 |
  | `tests/lint.test.sh` | 源码树一致性：Agent / 工作流 / 技能 / 路由契约验证 |

  运行全部测试：

  ```bash
  bash tests/install.test.sh && bash tests/lint.test.sh
  ```

  ---
  END OF README.zh.md CONTENT
  ---

- [ ] **Step 3: Verify structure matches README.md**

  ```bash
  grep -c "^## " README.zh.md && grep -c "^## " README.md
  ```
  Expected: same count (`13`) for both files

- [ ] **Step 4: Verify verbatim code blocks preserved**

  ```bash
  grep "aurorie-co/AURORIE-TEAMS" README.zh.md
  grep "artifacts/product/prd.md" README.zh.md
  grep "img.shields.io/badge/agents-34" README.zh.md
  ```
  Expected: all three lines present and identical to README.md

- [ ] **Step 5: Verify key ZH translations present**

  ```bash
  grep "没有你的确认" README.zh.md
  grep "我们重视一致性" README.zh.md
  grep "复制并运行" README.zh.md
  ```
  Expected: all three lines present

- [ ] **Step 6: Run lint tests**

  ```bash
  bash tests/lint.test.sh 2>&1 | tail -4
  ```
  Expected: `Failed: 0`

- [ ] **Step 7: Commit**

  ```bash
  git add README.zh.md
  git commit -m "docs(readme): add synchronized ZH translation"
  ```

---

### Task 5: Final verification and push

**Files:** None (verification only)

- [ ] **Step 1: Run both test suites**

  ```bash
  bash tests/install.test.sh 2>&1 | tail -4 && bash tests/lint.test.sh 2>&1 | tail -4
  ```
  Expected: `Failed: 0` for both

- [ ] **Step 2: Verify working tree is clean**

  ```bash
  git status
  ```
  Expected: `nothing to commit, working tree clean`
  If there are uncommitted changes, commit them:
  ```bash
  git add README.md README.zh.md
  git commit -m "docs(readme): final fixups"
  ```

- [ ] **Step 3: Push to remote**

  ```bash
  git push origin main
  ```
  Expected: push succeeds
