# P0 — Naming Cleanup + Path Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate the `engineer-lead` / `engineer.md` naming drift from user-facing files and add a formal workspace path schema to README so onboarding is unambiguous.

**Architecture:** Two focused edits — `templates/CLAUDE.md.template` and `tests/install.test.sh` — plus a path schema block added to `README.md` and `README.zh.md`. Historical plan docs in `docs/plans/` are left untouched (they are read-only artifacts, not user-facing content).

**Tech Stack:** bash, markdown

---

## File Map

| File | Action | What changes |
|------|--------|-------------|
| `templates/CLAUDE.md.template` | Modify | Replace `engineer-lead` with `backend-lead`; update cross-team example to `product → backend` |
| `tests/install.test.sh` | Modify | Replace `engineer.md` with `backend.md` in the workflow-preservation test |
| `README.md` | Modify | Add "Workspace layout" section with formal `{task_id}` path schema and real directory tree |
| `README.zh.md` | Modify | Mirror the same section in Chinese |

---

### Task 1: Fix `templates/CLAUDE.md.template`

**Files:**
- Modify: `templates/CLAUDE.md.template`

- [ ] **Step 1: Read the file**

  Read `templates/CLAUDE.md.template` and confirm the two occurrences of `engineer-lead`.

- [ ] **Step 2: Apply fix**

  Replace every instance of `engineer-lead` with `backend-lead` in the direct-invocation example.
  Replace `product-lead` with `aurorie-product-lead` and `engineer-lead` with `aurorie-backend-lead` in the sequential workflow example to match the real agent naming convention.

  Target result for the "To invoke" line:
  ```
  To invoke: use the `orchestrator` agent for most tasks, or invoke a team lead
  directly (e.g., `aurorie-backend-lead`) for single-team work.
  ```

  Target result for the Sequential Workflow example:
  ```markdown
  ### Feature Development (Product → Backend)
  1. Invoke `aurorie-product-lead` to write a PRD.
     When complete, find the actual task-id in `.claude/workspace/tasks/` and note the artifact path.
  2. Invoke `aurorie-backend-lead` with:
     `input_context: "artifact: .claude/workspace/artifacts/product/<actual-task-id>/prd.md\nImplement the features described in the PRD."`
     Replace `<actual-task-id>` with the UUID written by step 1.
  ```

- [ ] **Step 3: Verify no remaining `engineer-lead` references in user-facing files**

  Run:
  ```bash
  grep -r "engineer-lead\|engineer\.md" templates/ README.md README.zh.md CLAUDE.md
  ```
  Expected: no output (zero matches).

- [ ] **Step 4: Commit**

  ```bash
  git add templates/CLAUDE.md.template
  git commit -m "fix: update CLAUDE.md template to use aurorie-backend-lead (remove engineer-lead drift)"
  ```

---

### Task 2: Fix `tests/install.test.sh` workflow-preservation test

**Files:**
- Modify: `tests/install.test.sh`

- [ ] **Step 1: Read the relevant test block**

  Locate the `=== Test: workflow skipped if exists ===` block. It currently uses:
  ```bash
  echo "custom workflow" > .claude/workflows/engineer.md
  ...
  assert_file_contains "custom workflow preserved" ".claude/workflows/engineer.md" "custom workflow"
  ```

- [ ] **Step 2: Apply fix**

  Replace `engineer.md` with `backend.md` in both lines of that test block. The test intent is unchanged — it just needs to use a real team name that the installer actually touches.

  New block:
  ```bash
  echo ""
  echo "=== Test: workflow skipped if exists ==="
  echo "custom workflow" > .claude/workflows/backend.md
  "$REPO_ROOT/install.sh" > /dev/null
  assert_file_contains "custom workflow preserved" ".claude/workflows/backend.md" "custom workflow"
  ```

- [ ] **Step 3: Run the tests to confirm they still pass**

  ```bash
  bash tests/install.test.sh
  ```
  Expected output ends with: `Failed: 0`

- [ ] **Step 4: Commit**

  ```bash
  git add tests/install.test.sh
  git commit -m "fix: update install test to use backend.md instead of engineer.md"
  ```

---

### Task 3: Add workspace path schema to README.md

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`

- [ ] **Step 1: Write the new "Workspace Layout" section**

  Insert the following section into `README.md` **after** the "How it works" section and **before** the "Customizing" section:

  ```markdown
  ## Workspace Layout

  All runtime files live under `.claude/workspace/` (gitignored). The canonical paths are:

  | Path | Description |
  |------|-------------|
  | `.claude/workspace/tasks/{task_id}.json` | Task descriptor written by orchestrator before dispatch |
  | `.claude/workspace/artifacts/{team}/{task_id}/` | Team output directory |
  | `.claude/workspace/artifacts/{team}/{task_id}/summary.md` | Final deliverable — always present after a completed task |

  Example after running a product task and a market task:

  \```
  .claude/workspace/
  ├── tasks/
  │   ├── 3f8a1c2d-0001-4b5e-9d6f-abc123def456.json   ← product task
  │   └── 7e2b9a4f-0002-4c8d-be12-def456abc789.json   ← market task
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
  \```

  Pass artifacts between teams using `artifact: <path>` in `input_context` — see the cross-team workflow tutorial above.
  ```

- [ ] **Step 2: Mirror in README.zh.md**

  Add the Chinese equivalent section in the same position:

  ```markdown
  ## 工作区目录结构

  所有运行时文件存放在 `.claude/workspace/`（已加入 .gitignore）。标准路径规范如下：

  | 路径 | 说明 |
  |------|------|
  | `.claude/workspace/tasks/{task_id}.json` | orchestrator 在派发前写入的任务描述文件 |
  | `.claude/workspace/artifacts/{team}/{task_id}/` | 团队输出目录 |
  | `.claude/workspace/artifacts/{team}/{task_id}/summary.md` | 最终交付物——任务完成后必然存在 |

  以下是执行过一次 product 任务和一次 market 任务后的目录结构示例：

  \```
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
  \```

  通过在 `input_context` 中写 `artifact: <路径>` 将产出物传递给其他团队——详见上方跨团队工作流教程。
  ```

- [ ] **Step 3: Verify both README files render cleanly**

  Check that the code blocks close correctly (no unclosed triple-backtick).

- [ ] **Step 4: Commit**

  ```bash
  git add README.md README.zh.md
  git commit -m "docs: add workspace path schema with real directory tree example to README"
  ```

---

### Task 4: Final verification

- [ ] **Step 1: Run full test suite**

  ```bash
  bash tests/install.test.sh
  ```
  Expected: `Failed: 0`

- [ ] **Step 2: Confirm no stale references remain**

  ```bash
  grep -r "engineer-lead\|engineer\.md" templates/ README.md README.zh.md CLAUDE.md tests/
  ```
  Expected: no output.

- [ ] **Step 3: Push**

  ```bash
  git push origin main
  ```
