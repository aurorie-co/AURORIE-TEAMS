# AURORIE TEAMS

> 一个交互式的、图感知的 AI 团队编排运行时——为构建者、创始人和高级用户而生。

**一条命令。真实产出文件。可恢复的执行。**

```
@orchestrator "Build a SaaS for AI agents marketplace"
```

⚡ 34 个 Agent · 10 个团队 · 1 个 Orchestrator · 100 tests green

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue?style=flat-square)
![Version](https://img.shields.io/badge/version-v0.6.0-blue?style=flat-square)
![Agents](https://img.shields.io/badge/agents-34-informational?style=flat-square)
![Teams](https://img.shields.io/badge/teams-10-informational?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

**语言：** [English](README.md) | 中文

---

## 和别的 agent 系统有什么不同

大多数 agent 系统跑完就忘。AURORIE TEAMS 把每次执行都当作一等公民——可解释、可恢复。

### 先决策，再执行

系统在做任何事之前，先决定*做什么*和*为什么这么做*。每条路由决策都有分数、可解释、可编程——不是黑盒。每次你都能看到哪些团队被选中、哪些是次要、为什么。

### 图感知执行

团队不是扁平的并行执行——基于 wave 的 DAG 决定执行顺序。依赖关系被显式表达，独立节点并行运行，部分失败被隔离。不会盲目跑。

### 跨任务协调

一个任务是一个 milestone。跨任务、跨 graph、跨时间追踪进度。中断了？从断点继续。想回看？Replay 检查任何历史执行。系统有记忆。

---

## 一个完整流程

```
@orchestrator "Build a SaaS for AI agents marketplace"
```

**Step 1 — 路由决策**
→ backend (high, score 4) → selected
→ product (medium, score 2) → secondary
→ frontend (medium, score 1) → secondary

**Step 2 — 决策策略**
→ `dispatch_policy.medium.when_high_exists: ignore` — secondary 团队被忽略

**Step 3 — Wave 执行**
```
Wave 1: [product-1]     → done          10:01:01
Wave 2: [backend-1]     → done          10:02:33
Wave 3: [frontend-1]   → completed      10:04:12
```

**输出：**
```
.claude/workspace/
├── tasks/<task-id>.json       # routing + execution graph + milestone ref
└── artifacts/
    ├── product/<task-id>/     # prd.md + summary.md
    ├── backend/<task-id>/    # implementation + summary.md
    └── frontend/<task-id>/    # implementation + summary.md
```

**不是一次性的。** 某处失败了，resume 而不是 restart。

---

## 运行时模式

AURORIE TEAMS 是一个交互式运行时。每种模式都是对同一执行状态的不同操作方式。

### `@orchestrator "prompt"` — 正常执行
完整路由 + 派发。团队写入 artifacts。Graph 被构建和追踪。

### `@orchestrator --debug "prompt"` — 查看完整 trace
每个分数、每个评估、每个置信度区间。在任何事运行之前，你能看到系统决定了什么、为什么。

### `@orchestrator --dry-run "prompt"` — 预览，不产生副作用
计算路由决策、查看执行图——但不派发任何团队。和 `--debug` 组合使用可以完整预览。

### `@orchestrator --milestone "Launch SaaS" "prompt"` — 跨任务追踪
将任务归入一个共享目标。用 `--milestone-status <id>` 查询聚合进度。状态汇总规则：`partial_failed > in_progress > completed > pending`。

### `@orchestrator --resolve <task-id> all|none|selective` — 解决暂停的决策
当任务暂停等待确认时，解决它——全部批准、全部拒绝、或选择性选择团队。幂等操作。

### `@orchestrator --replay <task-id>` — 检查历史执行（只读）
查看任何历史任务的路由决策、wave 时间线、节点状态、milestone 引用。无状态变更。

### `@orchestrator --resume <task-id>` — 从中断处继续
从部分状态继续 DAG。三条路径：
- **`in_progress`** — 从当前 wave 继续
- **`partial_failed`** — 仅重试失败的节点（done/blocked 不受影响）
- **`blocked`** — 重新检查 `artifacts_in`，仅解除已有 artifacts 的节点

每条 resume 路径在变更状态前都会提示确认。

---

## 系统模型

```
User Request → Orchestrator → Teams → Agents → Artifacts
                    ↓
              routing_decision (who + why)
                    ↓
              execution_graph (DAG + waves)
                    ↓
              milestone (cross-task coordination)
```

### Orchestrator
读取 `.claude/routing.json`。对每条团队规则打分。构建执行图。驱动派发。

### Teams（10 个领域）
每个团队是自包含单元：agents、workflows、skills、MCP 工具访问。

| 团队 | 专注领域 |
|------|---------|
| market | SEO、内容、Analytics |
| product | PM、UX、研究 |
| backend | 服务、数据层 |
| frontend | UI、React |
| infra | 部署、DevOps |
| data | 分析、数据管道 |
| design | 视觉、UX |
| mobile | iOS、Android |
| support | 帮助、文档 |
| research | 市场、竞品 |

### 执行图
基于 wave 的 DAG。依赖关系显式声明。节点在同一 wave 内并行运行。部分失败被隔离且可恢复。

### Artifacts
每个团队将结构化输出写入 `.claude/workspace/artifacts/<team>/<task-id>/`。每个任务有独立 UUID 文件夹——产出文件不会相互覆盖。

### Milestones
跨任务的持久协调层。任务在创建时附着到 milestone。Milestone 状态从所有附着任务聚合而来——不是控制信号。

---

## 安装

```bash
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh
```

然后：

```
@orchestrator "Build me a SaaS product from scratch"
```

**环境要求：** macOS 或 Linux · `jq` · `uuidgen` 或 `python3` · Node.js

**升级：**
```bash
git -C /tmp/aurorie-teams pull && /tmp/aurorie-teams/install.sh
```

---

## 试试看

### 构建产品 ⭐
```
@orchestrator "Create a SaaS for AI agents marketplace"
```
→ Product + Backend + Frontend → PRD、实现、UI

### 分析与调研
```
@orchestrator "Investigate why our DAU dropped 30% last week"
```
→ Data + Research → 分析报告

### 协调多任务目标
```
@orchestrator --milestone "Launch v1.0" "Build a crypto trading platform"
```
→ 第一个任务附着到 milestone → `--milestone-status <id>` 追踪所有后续任务进度

---

## 自定义

| 定制内容 | 路径 |
|---------|------|
| 团队路由规则 | `.claude/routing.json` |
| 派发策略（auto/ask/ignore） | `.claude/routing.json` → `dispatch_policy` |
| 团队工作流 | `.claude/workflows/<team>.md` |
| Agent 工具权限 | `.claude/settings.json` |

---

## ⚠️ 安全

- **Agent 只生成输出——不主动执行外部操作，除非你接入它们。**
  默认行为是将文件写入 `.claude/workspace/artifacts/`。
- **没有你的确认，什么都不会执行。** `ask` 模式会暂停等待确认。
- **尽量使用只读凭证。**
- 查看 `.claude/settings.json` 控制每个 Agent 的工具访问权限。

---

## 测试

**113/113 tests green** — 每次提交都绿。

```
bash tests/install.test.sh && bash tests/lint.test.sh
python3 tests/routing/test_routing_cases.py
python3 tests/routing/test_dispatch_policy.py
python3 tests/routing/test_replay_resume.py
```

---

## 路线图

**v0.6 — 持久化执行运行时**（当前版本）
- [x] Replay — 只读执行检查
- [x] Resume — 从部分状态继续 DAG
- [x] 状态优先级不变式 — `pending_decision` 始终阻止 resume
- [x] 局部失败恢复 — 仅 failed 节点重置
- [x] 阻塞节点恢复 — unblock 前重新检查 `artifacts_in`

**v0.5 — 目标导向协调运行时**
- [x] Milestone 系统 — 跨任务追踪和聚合
- [x] 选择性路由 — 选择性批准部分 medium 团队

**v0.4 — 交互路由合约 + DAG 执行**
- [x] `pending_decision` schema + resolve 接口
- [x] 基于 wave 的 DAG 派发、并行节点、部分失败

**长期 — AI 原生公司**
- [ ] 可观测性控制台
- [ ] 自动重试
- [ ] 跨任务 resume
- [ ] Agent 市场

---

## 参与贡献

我们在构建 AI 公司操作系统——有主张，且公开。

参与前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。
