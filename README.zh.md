# AURORIE TEAMS

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ██████╗██╗  ██╗ █████╗ ██████╗ ██████╗ ██╗   ██╗██████╗  │
│  ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗ │
│  ╚█████╗ ███████║███████║██████╔╝██████╔╝ ╚████╔╝ ██████╔╝ │
│   ╚═══██╗██╔══██║██╔══██║██╔═══╝ ██╔═══╝   ╚██╔╝  ██╔══██╗ │
│  ██████╔╝██║  ██║██║  ██║██║     ██║        ██║   ██████╔╝ │
│  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝        ╚═╝   ╚═════╝  │
│                                                                 │
│   ███████╗██╗██╗  ██╗████████╗██████╗  ██████╗ ███╗   ███╗  │
│   ╚══███╔╝╚██╗██╔╝╚██╗██╔╝╚══██╔══╝██╔══██╗██╔═══██╗████╗ ████║│
│     ███╔╝  ╚███╔╝  ╚███╔╝    ██║   ██████╔╝██║   ██║██╔████╔██║│
│    ███╔╝   ██╔██╗  ██╔██╗    ██║   ██╔══██╗██║   ██║██║╚██╔╝██║│
│   ███████╗██╔╝ ██╗██╔╝ ██╗   ██║   ██║  ██║╚██████╔╝██║ ╚═╝ ██║│
│   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

> **AI 团队编排运行时——不会遗忘。**

`一条命令` → `团队分派` → `文件产出` → `执行可追踪 + 可恢复`

---

### 快速状态

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue?style=flat-square&logo=apple&logoColor=white)
![Version](https://img.shields.io/badge/version-v0.6.0-222?style=flat-square&logo=semantic-release&logoColor=white)
![Tests](https://img.shields.io/badge/tests-113%2F113%20green-222?style=flat-square&logo=github-actions&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## 它做什么

```
@aurorie-orchestrator "Build a SaaS for AI agents marketplace"

  → 路由:    backend ■■■■■■■■■■■■■■■■■■■■■ high
             product ■■■■■■ medium
             frontend ■■■■ medium

  → 策略:    auto (high) · ignore (medium, high exists)

  → 图:      [product-1] → [backend-1]
                           ↘ [frontend-1]

  → 输出:    .claude/workspace/artifacts/{backend,frontend,product}/<task-id>/
```

**不是一次性的。** 如果 `backend-1` 失败了：

```
@aurorie-orchestrator --resume <task-id>

  检测到 partial_failed — 仅重试失败的节点

  Wave 1: [product-1]     ■■■■■■■■■■■■■■■ done
  Wave 2: [backend-1]     重试 ■■■■■■■■■■■ running   ← 只有这个
  Wave 3: [frontend-1]   (等待 backend) — 跳过

  → 只有 backend 重跑了，frontend 保持 done 状态
```

---

## 三个核心差异

| | | |
|---|---|---|
| **先决策** | **图感知执行** | **跨任务记忆** |
| 每条路由决策都有分数、可解释、可编程。运行前你能看到每个团队为什么被选中、是次要还是被过滤。 | 团队按 wave-based DAG 顺序执行。依赖关系显式声明。部分失败被隔离。不会盲目跑。 | Milestone 跨任务和时间追踪进度。Replay 检查任何历史执行。Resume 从中断处继续。 |
| `+API +endpoint +SaaS → score 4 → high → dispatched` | `product → backend → frontend` (线性) | `@aurorie-orchestrator --replay <task-id>` |
| `+requirements +SaaS → score 2 → medium → secondary` | `research → [backend, frontend]` (并行扇出) | `@aurorie-orchestrator --resume <task-id>` |
| `+iOS → score −2 → filtered` | 阻塞节点等待，done 节点保持 | `--milestone-status <id>` |

---

## 运行时命令参考

| 命令 | 功能 |
|------|------|
| `@aurorie-orchestrator "prompt"` | 完整路由 + 分派 + artifact 输出 |
| `@aurorie-orchestrator --debug "prompt"` | 运行前查看每条分数、评估和决策 |
| `@aurorie-orchestrator --dry-run "prompt"` | 预览路由 + 图，但不实际分派 |
| `@aurorie-orchestrator --milestone "目标" "prompt"` | 运行并附加 milestone 追踪 |
| `@aurorie-orchestrator --milestone-status <id>` | 查询聚合 milestone 进度 |
| `@aurorie-orchestrator --resolve <task-id> all\|none\|selective` | 解决暂停的决策（幂等） |
| `@aurorie-orchestrator --replay <task-id>` | 只读：检查历史路由 + 执行图 |
| `@aurorie-orchestrator --resume <task-id>` | 继续：`in_progress` · `partial_failed` · `blocked` |

---

## 系统架构

```
    ┌──────────────────────────────────────────────────────┐
    │                     Orchestrator                      │
    │  routing.json → 团队打分 → 构建 DAG → 分派          │
    └────────────────────────┬─────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
     ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
     │ Backend  │      │Frontend │      │ Product │
     │  Team    │      │  Team  │      │  Team   │
     └────┬────┘      └────┬────┘      └────┬────┘
          │                  │                  │
     ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
     │ developer│      │developer│      │    PM   │
     │   QA    │      │  devops │      │    UX   │
     └─────────┘      └─────────┘      └─────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │    Artifacts      │
                    │ .claude/workspace│
                    └─────────────────┘
```

**团队：** market · product · backend · frontend · infra · data · design · mobile · support · research

---

## 安装

```bash
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh

@aurorie-orchestrator "Build me a SaaS product from scratch"
```

环境要求：macOS 或 Linux · `jq` · `uuidgen` 或 `python3` · Node.js

---

## 三条命令

```bash
# 1. 构建产品 (触发 Product + Backend + Frontend)
@aurorie-orchestrator "Create a SaaS for AI agents marketplace"
```

```bash
# 2. 分析下跌 (触发 Data + Research)
@aurorie-orchestrator "Investigate why our DAU dropped 30% last week"
```

```bash
# 3. 协调多任务里程碑
@aurorie-orchestrator --milestone "Launch v1.0" "Build the crypto trading platform"
# ... 然后继续附加更多任务到同一个 milestone
@aurorie-orchestrator --milestone-status ms_abc123
```

---

## 自定义

| 定制内容 | 路径 |
|----------|------|
| 团队路由规则 | `.claude/routing.json` |
| 分派策略 (auto / ask / ignore) | `.claude/routing.json` → `dispatch_policy` |
| 团队工作流 | `.claude/workflows/<team>.md` |
| Agent 工具权限 | `.claude/settings.json` |

---

## 安全

- **Agent 只写文件——不主动执行外部操作，除非你接入。** 默认：`.claude/workspace/artifacts/`
- **没有你的确认什么都不执行。** `ask` 模式在分派前暂停等待确认
- **尽量使用只读凭证**

---

## 测试

**113/113 tests green** — 每次提交都绿。

```bash
bash tests/install.test.sh && bash tests/lint.test.sh
python3 tests/routing/test_routing_cases.py
python3 tests/routing/test_dispatch_policy.py
python3 tests/routing/test_replay_resume.py
```

---

## 路线图

### v0.6 — 持久化执行运行时 _(当前版本)_
- [x] Replay — 只读执行检查
- [x] Resume — 从部分状态继续 DAG
- [x] 状态优先级不变式 — `pending_decision` 始终阻止 resume
- [x] 局部失败恢复 — 仅 failed 节点重置
- [x] 阻塞节点恢复 — unblock 前重新检查 `artifacts_in`

### v0.5 — 目标导向协调运行时
- [x] Milestone 系统 — 跨任务追踪和聚合
- [x] 选择性路由 — 选择性批准部分 medium 团队

### v0.4 — 交互路由合约 + DAG 执行
- [x] `pending_decision` schema + resolve 接口
- [x] 基于 wave 的 DAG 分派、并行节点、部分失败

### 长期
- [ ] 可观测性控制台
- [ ] 自动重试
- [ ] 跨任务 resume
- [ ] Agent 市场

---

**有主张的默认配置，所有内容皆可定制。**
