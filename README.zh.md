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
   - Backend Team（服务与数据层）
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
    ├── backend/implementation.md
    ├── frontend/frontend-implementation.md
    └── mobile/ios-implementation.md
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
→ Data     (+score: dropped, metrics, root cause)
→ Research (+score: why did, investigate)
→ Backend  (no match)
Final: Data + Research

"Build a crypto SaaS with React dashboard"
→ Frontend (+score: SaaS, React)
→ Backend  (+score: SaaS)
→ Product  (+score: SaaS)
→ Data     (+score: dashboard)
Final: Frontend + Backend + Product + Data
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
export POSTGRES_URL=...

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
.claude/workspace/artifacts/backend/implementation.md
.claude/workspace/artifacts/frontend/frontend-implementation.md
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
.claude/workspace/artifacts/research/research-report.md
```

复制并运行——你会得到真实的产出文件。

---

### 构建 App

```
@orchestrator "Design a mobile app for habit tracking with iOS and Android support"
```

触发团队：
- Mobile Team
- Product Team

输出：
```
.claude/workspace/artifacts/mobile/ios-implementation.md
.claude/workspace/artifacts/mobile/android-implementation.md
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
.claude/workspace/artifacts/research/comparison-matrix.md
.claude/workspace/artifacts/research/summary.md
```

复制并运行——你会得到真实的产出文件。

---

### 构建交易系统

```
@orchestrator "Build a crypto SaaS with real-time price feeds, portfolio analytics, and a React dashboard"
```

触发团队：
- Product Team
- Backend Team
- Frontend Team
- Data Team

输出：
```
.claude/workspace/artifacts/product/prd.md
.claude/workspace/artifacts/backend/implementation.md
.claude/workspace/artifacts/frontend/frontend-implementation.md
.claude/workspace/artifacts/data/report-spec.md
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
