# aurorie-teams

![平台](https://img.shields.io/badge/平台-macOS%20%7C%20Linux-blue?style=flat-square)
![Agents](https://img.shields.io/badge/agents-34-informational?style=flat-square)
![Teams](https://img.shields.io/badge/teams-10-informational?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

公司级 Claude Code 多智能体配置库。
10 个团队，34 个 agent，一键安装到任意项目。

**语言：** [English](README.md) | 中文

---

## 快速开始

```bash
# 1. 克隆库
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams

# 2. 安装到你的项目
cd /path/to/your-project && /tmp/aurorie-teams/install.sh

# 3. 调用 orchestrator
# 在 Claude Code 中：@orchestrator 写一篇关于我们新 API 发布的博客文章。
```

---

## 概览

aurorie-teams 为你的 Claude Code 环境提供一套完整的公司组织架构——每个团队都有一个 Lead agent 负责任务路由、协调 specialist 输出，并在最后写入 `summary.md`。各团队可独立运行，也可通过 artifact 链路跨团队协作。

### 架构图

```mermaid
graph TD
    U([用户请求]) --> O[orchestrator<br/>读取 routing.json]
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

### 团队一览

| 团队 | Agent 数 | 职责 |
|------|---------|------|
| `market` | 4 | 博客/落地页写作、SEO 审计、营销分析、内容优化 |
| `product` | 4 | PRD、UX 设计说明、市场调研、路线图规划 |
| `research` | 3 | 深度调研、竞品分析、综合报告 |
| `support` | 4 | 工单分类、客户回复草稿、升级协调 |
| `frontend` | 4 | UI 实现、组件审查、前端 CI/CD |
| `mobile` | 5 | iOS/Android 功能开发、跨平台审查、发布流程 |
| `backend` | 4 | API 开发、数据库、后端基础设施 |
| `infra` | 3 | Terraform 模块编写、IaC 审查、PR Review、基础设施审计 |
| `design` | 3 | 设计系统（token、组件规范、WCAG 无障碍）、品牌视觉规范 |
| `data` | 4 | 数据分析、ETL 管道、数据看板 |

---

## 环境要求

| 依赖 | 安装方式 |
|------|---------|
| macOS 或 Linux（bash 3.2+） | — |
| `jq` | `brew install jq` / `apt install jq` |
| `uuidgen` 或 `python3` | 大多数系统已预装 |
| Node.js | 用于 `npx` MCP 服务器 |

---

## 安装

在你的项目根目录执行：

```bash
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh
```

执行后会将 34 个 agent、27 个 skill 和 10 个 workflow 文件安装到项目的 `.claude/` 目录。

### 安装参数

| 参数 | 效果 |
|------|------|
| （无） | 默认安装 |
| `--force-workflows` | 覆盖本地已修改的 workflow 和 routing.json（会提示确认） |
| `--yes` | 跳过所有确认提示（适合 CI 环境） |
| `--detect-orphans` | 报告仓库中已不存在的本地 agent/skill 文件 |

### 升级

```bash
cd /tmp/aurorie-teams && git pull
cd /path/to/your-project && /tmp/aurorie-teams/install.sh
```

`.claude/workflows/` 和 `.claude/routing.json` 的本地修改在升级时会被保留（除非使用 `--force-workflows`）。

---

## 环境变量

在启动 Claude Code 前配置到 shell profile 中：

```bash
export GITHUB_TOKEN=...        # GitHub API — 所有团队通过 shared MCP 使用
export EXA_API_KEY=...         # Exa 神经搜索 — market、product、research 团队
export FIRECRAWL_API_KEY=...   # Web 爬取 — market、research 团队
export POSTGRES_URL=...        # PostgreSQL 连接串 — backend、data 团队
                               # 格式：postgresql://user:password@host:5432/dbname
```

---

## MCP 服务器

MCP 服务器按团队预配置，安装时合并到 `.claude/settings.json`。只包含团队核心工作所需的服务器。

| 服务器 | 包名 | 适用团队 |
|--------|------|---------|
| `github` | `@modelcontextprotocol/server-github` | 所有团队（共享） |
| `exa` | `exa-mcp-server` | market、product、research（共享） |
| `firecrawl` | `firecrawl-mcp` | market、research |
| `puppeteer` | `@modelcontextprotocol/server-puppeteer` | market |
| `playwright` | `@playwright/mcp` | frontend |
| `postgres` | `@modelcontextprotocol/server-postgres` | backend、data |
| `sqlite` | `@modelcontextprotocol/server-sqlite` | data |

`filesystem` 服务器被有意排除——agent 通过 Claude Code 内置的 Read/Write/Edit/Glob/Grep 工具访问文件系统。

---

## 使用教程

### 1. 通过 orchestrator 调用团队

推荐入口是 `orchestrator` agent。它读取 `.claude/routing.json`，将请求匹配到对应团队，然后派发团队 Lead。

在 Claude Code 中：

```
@orchestrator 写一篇关于我们新 API 发布的博客文章。
目标受众：开发者。目标：促进注册转化。
```

orchestrator 会把这个任务路由到 `aurorie-market-lead`，后者派发 SEO 和 content specialist，最后写 `summary.md` 汇总交付物路径。

---

### 2. 直接调用团队 Lead

如果你明确知道要用哪个团队，可以跳过 orchestrator：

```
@aurorie-market-lead 写一篇关于我们新 API 发布的博客文章。
目标受众：开发者。目标：促进注册转化。
```

---

### 3. 示例：内容创作（market 团队）

**请求：**
```
@aurorie-market-lead
为我们的移动端 SDK 写一个落地页。
目标受众：iOS/Android 开发者。
目标：试用注册。
需要 SEO 优化。
```

**执行过程：**
1. `aurorie-market-lead` 读取 brief，检测到「落地页」— 必须先派发 SEO
2. `aurorie-market-seo` 进行关键词研究，写 `seo-report.md`
3. `aurorie-market-content` 基于 SEO 报告写落地页，写 `content.md`
4. Lead 审查后写 `summary.md`

**产出文件：**
```
.claude/workspace/artifacts/market/<task-id>/
  seo-report.md       <- 关键词研究、页面优化建议
  content.md          <- 落地页文案
  summary.md          <- Lead 的最终汇总
```

---

### 4. 示例：支持工单（support 团队）

**请求：**
```
@aurorie-support-lead
客户工单："我导出了数据，但文件是空的。已试了 3 次。"
账户：Pro 套餐，使用 2 年。此前没有导出相关工单。
```

**执行过程：**
1. `aurorie-support-triage` 分类：Bug / P1 — 主要功能故障，无 workaround
2. `aurorie-support-responder` 以 P1 语气起草回复，包含下一步说明
3. Lead 审查后写 `summary.md`

**如果 triage 返回 P0：** Lead 还会额外派发 `aurorie-support-escalation`，生成 `escalation-plan.md` 后再发出客户回复。

**产出文件：**
```
.claude/workspace/artifacts/support/<task-id>/
  triage-report.md    <- 类别、优先级、根因假设
  response-draft.md   <- 客户回复草稿、语气说明、发送渠道建议
  summary.md          <- Lead 的最终汇总
```

---

### 5. 示例：跨团队工作流（product → frontend）

团队之间可以通过 `input_context` 中的 `artifact:` 行传递产出物实现链路协作。

**第一步 — Product 团队写 PRD：**
```
@aurorie-product-lead
写一个深色模式功能的 PRD。
用户希望在移动端支持深色模式。工程预估：1 个 sprint。
```

产出 `.claude/workspace/artifacts/product/<task-id>/prd.md`。

**第二步 — Frontend 团队基于 PRD 实现：**
```
@aurorie-frontend-lead
按照 PRD 中的描述实现深色模式功能。
input_context:
artifact: .claude/workspace/artifacts/product/<实际-task-id>/prd.md
```

Frontend lead 读取 PRD artifact，然后路由给 developer 和 QA specialist。

---

### 6. 示例：内容表现优化重写（market 团队）

当已有内容表现下滑时，market 团队可以一次请求完成完整的诊断和重写：

```
@aurorie-market-lead
我们的博客文章"API 入门指南"月访问量从 6 个月前的 800 降至现在的 200，
竞品发布了 SEO 更好的同类文章后，有机流量明显下降。

数据：
- 当前：200 次/月，"api getting started guide" 排名第 18 位
- 历史：800 次/月，排名第 6 位
- CTR：1.2%（原为 4.8%）

请重写这篇文章以恢复排名。
```

**执行过程：**
1. Analytics 诊断流量下降原因（关键词排名下滑、CTR 衰减）
2. SEO 找出与竞品的关键词差距
3. Content 综合两份报告重写文章
4. Lead 写 `summary.md`，包含原始问题、改动说明和预期恢复效果

---

### 7. 示例：深度调研（research 团队）

**请求：**
```
@aurorie-research-lead
调研 AI 代码生成工具市场：主要竞品（GitHub Copilot、Cursor、Tabnine），
各自的定价、差异化、用户评价。
目标：为我们的产品路线图决策提供参考。
```

**执行过程：**
1. `aurorie-research-web` 通过 Exa/Firecrawl 进行网络搜索，收集数据
2. `aurorie-research-synthesizer` 将原始数据综合成结构化报告
3. Lead 审查后写 `summary.md`，包含核心洞察和建议动作

**产出文件：**
```
.claude/workspace/artifacts/research/<task-id>/
  research-notes.md   <- 原始数据来源、数据点、引用
  research-report.md  <- 综合研究报告、竞品图谱
  summary.md          <- Lead 的核心洞察和建议动作
```

---

## 自定义配置

- **工作流：** 编辑 `.claude/workflows/<team>.md` 修改团队工作方式
- **路由规则：** 编辑 `.claude/routing.json` 控制关键词与团队的映射关系
- **项目背景：** 编辑项目根目录的 `CLAUDE.md`，所有 agent 都会读取该文件获取项目上下文

`.claude/workflows/` 和 `.claude/routing.json` 的本地修改在升级时会被保留（除非使用 `--force-workflows`）。

---

## 工作原理

每个团队都遵循相同的模式：

```
用户请求
    └── orchestrator（读取 routing.json）
            └── 团队 Lead（读取 workflow，派发 specialist）
                    ├── specialist A --> artifact A
                    ├── specialist B --> artifact B
                    └── Lead 写 summary.md
```

**任务文件** `.claude/workspace/tasks/<task-id>.json` — 在 agent 之间传递任务描述和 `input_context`。

**产出文件** `.claude/workspace/artifacts/<team>/<task-id>/` — 团队的交付物。通过 `input_context` 中的 `artifact: <path>` 传递给其他团队。

**`summary.md`** — 每个工作流的最终输出，由 Lead 在审查所有 specialist 产出后写入。这是对外分享的标准交付物。

---

## 工作区目录结构

所有运行时文件存放在 `.claude/workspace/`（已加入 .gitignore）。标准路径规范如下：

| 路径 | 说明 |
|------|------|
| `.claude/workspace/tasks/{task_id}.json` | orchestrator 在派发前写入的任务描述文件 |
| `.claude/workspace/artifacts/{team}/{task_id}/` | 团队输出目录 |
| `.claude/workspace/artifacts/{team}/{task_id}/summary.md` | 最终交付物——任务完成后必然存在 |

以下是执行过一次 product 任务和一次 market 任务后的目录结构示例：

```
.claude/workspace/
├── tasks/
│   ├── 3f8a1c2d-0001-4b5e-9d6f-abc123def456.json   ← product 任务
│   └── 7e2b9a4f-0002-4c8d-be12-def456abc789.json   ← market 任务
└── artifacts/
    ├── product/
    │   └── 3f8a1c2d-0001-4b5e-9d6f-abc123def456/
    │       ├── prd.md
    │       └── summary.md
    └── market/
        └── 7e2b9a4f-0002-4c8d-be12-def456abc789/
            ├── seo-report.md
            ├── content.md
            └── summary.md
```

通过在 `input_context`中写 `artifact: <路径>` 将产出物传递给其他团队——详见上方跨团队工作流教程。
