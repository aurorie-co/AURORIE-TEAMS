# Confidence-Based Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add confidence bands, conditional dispatch, and structured routing explanation to the orchestrator so routing decisions are explainable, observable, and policy-driven.

**Architecture:** `routing.json` gains a `routing_policy` block that defines candidate and confidence thresholds. `orchestrator.md` replaces its Routing section with an 8-step decision pipeline: read policy → score → filter → sort → band → dispatch → record → summarize. Every task JSON gains an optional `routing_decision` field with the full decision record.

**Tech Stack:** JSON (routing config), Markdown (agent prompt), no external dependencies.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `.claude/routing.json` | Modify | Add `routing_policy` top-level block |
| `.claude/agents/orchestrator.md` | Modify | Replace Routing section with 8-step pipeline |

---

## Task 1: Add `routing_policy` to routing.json

**Files:**
- Modify: `.claude/routing.json`

- [ ] **Step 1: Read the current routing.json**

  Open `.claude/routing.json` and confirm the top-level keys are `version`, `rules`, and `fallback`.

- [ ] **Step 2: Add routing_policy block**

  Insert the following as a top-level key between `"version"` and `"rules"`:

  ```json
  "routing_policy": {
    "candidate_threshold": 1,
    "confidence_thresholds": {
      "high": 3,
      "medium": 1
    }
  },
  ```

  The final file structure should be:

  ```json
  {
    "version": "2",
    "routing_policy": {
      "candidate_threshold": 1,
      "confidence_thresholds": {
        "high": 3,
        "medium": 1
      }
    },
    "rules": [ ... ],
    "fallback": "orchestrator-clarify"
  }
  ```

- [ ] **Step 3: Validate JSON is well-formed**

  Run:
  ```bash
  python3 -c "import json; json.load(open('.claude/routing.json')); print('valid')"
  ```
  Expected output: `valid`

- [ ] **Step 4: Commit**

  ```bash
  git add .claude/routing.json
  git commit -m "feat(routing): add routing_policy with confidence thresholds"
  ```

---

## Task 2: Replace Routing section in orchestrator.md

**Files:**
- Modify: `.claude/agents/orchestrator.md`

- [ ] **Step 1: Read the current orchestrator.md**

  Open `.claude/agents/orchestrator.md`. The section to replace starts at `## Routing` and ends before `## Sequential Cross-Team Workflows`. Everything between those headers gets replaced.

- [ ] **Step 2: Replace the Routing section**

  Replace the entire `## Routing` section (lines 10–70 in the current file) with the following:

  ````markdown
  ## Routing

  ### Step 1 — Read policy

  Read `.claude/routing.json`. Extract `routing_policy`. If the field is missing or incomplete, apply these defaults:
  - `candidate_threshold = 1`
  - `confidence_thresholds.high = 3`
  - `confidence_thresholds.medium = 1`

  ### Step 2 — Score each team

  For each rule in `rules[]`, compute:

  ```
  net_score = count(positive_keywords matched in request) - 2 × count(negative_keywords matched in request)
  ```

  Matching rules:
  - Case-insensitive
  - Token-based partial match: "auth" matches "authentication"; "api" does NOT match "capability"
  - Negative matches apply per-team only — they do not suppress other teams
  - Each team's score is computed independently

  Record `matched_positive[]` and `matched_negative[]` for each team.

  ### Step 3 — Candidate filter

  ```
  if net_score < candidate_threshold → filtered_teams (stop processing this team)
  else → candidate pool
  ```

  ### Step 3.5 — Sort candidate pool

  Sort all candidates by:
  1. `net_score` descending
  2. `matched_positive` count descending
  3. `matched_negative` count ascending

  ### Step 4 — Assign confidence bands

  For each candidate:
  ```
  if net_score >= thresholds.high   → confidence = "high"
  elif net_score >= thresholds.medium → confidence = "medium"
  ```

  ### Step 5 — Conditional dispatch

  ```
  if any high candidates exist:
      selected_teams = all high candidates (sorted order)
      secondary_teams = all medium candidates
      dispatch_strategy = "conditional"

  elif any medium candidates exist:
      selected_teams = all medium candidates (sorted order)
      secondary_teams = []
      dispatch_strategy = "conditional"

  else:
      → FALLBACK (Step 6)
  ```

  When `selected_teams` contains multiple teams, dispatch them in parallel (Step B).
  When `selected_teams` contains one team, use single dispatch (Step A).

  ### Step 6 — Fallback

  Triggered when no candidates survive Step 3:
  - Do NOT dispatch any team
  - Do NOT generate any artifact
  - Generate one task-id, write task JSON with `status = "needs_clarification"` and `routing_decision.selected_teams = []`
  - Output exactly one clarifying question — no preamble, no explanation, just the question (e.g. "Is this a backend API task or a UI feature?")
  - Re-evaluate routing when the user replies

  ### Step 7 — Write routing_decision to task JSON

  Add `routing_decision` alongside existing task fields. Compute `top_signals` as the deduplicated union of `matched_positive` from `selected_teams`, sorted by frequency then by score contribution, top 3–5 terms.

  ```json
  "routing_decision": {
    "routing_schema_version": "v0.2",
    "policy_snapshot": {
      "candidate_threshold": 1,
      "confidence_thresholds": {
        "high": 3,
        "medium": 1
      },
      "dispatch_policy": {
        "high": "selected",
        "medium_when_high_exists": "secondary",
        "medium_when_no_high_exists": "selected",
        "low": "filtered"
      }
    },
    "dispatch_strategy": "conditional",
    "top_signals": ["<top matched keywords from selected_teams, max 5>"],
    "selected_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "high",
        "matched_positive": [],
        "matched_negative": []
      }
    ],
    "secondary_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "medium",
        "matched_positive": [],
        "matched_negative": []
      }
    ],
    "filtered_teams": [
      {
        "team": "<team-id>",
        "score": 0,
        "confidence": "low",
        "matched_positive": [],
        "matched_negative": []
      }
    ]
  }
  ```

  Always use the actual `routing_policy` values from the current `routing.json` when writing `policy_snapshot` — not hardcoded values.

  ### Step 8 — Output user summary

  **When high teams exist:**
  ```
  Routed to:
  - <team> (high, score <N>)

  Also relevant (not dispatched):
  - <team> (medium, score <N>)

  Reason: matched "<signal1>", "<signal2>".
  ```

  Omit the "Also relevant" block entirely if `secondary_teams` is empty.

  **When only medium teams exist:**
  ```
  Routed to:
  - <team> (medium, score <N>)

  No high-confidence teams found.

  Reason: matched "<signal1>", "<signal2>".
  ```

  Rules:
  - Reason line uses `top_signals` only — do not write free-form explanation text
  - Filtered teams are NOT listed in the summary
  - Summary is printed before dispatch begins

  ### Step A — Single Dispatch

  1. Generate task-id: `uuidgen | tr '[:upper:]' '[:lower:]'`
     Fallback: `python3 -c "import uuid; print(uuid.uuid4())"`
  2. Write task file to `.claude/workspace/tasks/<task-id>.json` with fields: `task_id`, `created_at` (ISO8601), `description`, `assigned_team`, `status: "pending"`, `input_context: ""`, `artifact_path`, and `routing_decision`.
  3. Invoke team lead via Agent tool:
     ```
     Task file: .claude/workspace/tasks/<task-id>.json

     You are a coordinator. Do NOT write the deliverable yourself.

     1. Read `.claude/workflows/<team>.md` FIRST to determine your execution steps.
     2. Dispatch each workflow step as a sub-agent using the Agent tool.
     3. After all sub-agents complete, collect their output artifact paths.
     4. Apply the file-handoff skill to write `summary.md` under the artifact path.
     5. Return the contents of `summary.md` as your response (max 400 words).
     ```
  4. Return Agent tool result to user.

  ### Step B — Parallel Dispatch

  1. Generate one task-id per selected team.
  2. Write one task file per team (each with its own `routing_decision`).
  3. Invoke all team leads simultaneously via parallel Agent tool calls using the Step A prompt template.
  4. Await all responses.
  5. Synthesize summaries. Return combined summary to user.
  ````

- [ ] **Step 3: Verify the file is well-formed**

  Read the file back and confirm:
  - `## Routing` section is present
  - `## Sequential Cross-Team Workflows` section is still present and unchanged
  - `## Failure Handling` section is still present and unchanged
  - No duplicate section headers

- [ ] **Step 4: Commit**

  ```bash
  git add .claude/agents/orchestrator.md
  git commit -m "feat(orchestrator): confidence-based routing pipeline (v0.2.0)"
  ```

---

## Task 3: Validate all 5 routing cases

Run each prompt via `@orchestrator` and verify both the terminal summary and the task JSON written to `.claude/workspace/tasks/`.

- [ ] **Case 1 — High only**

  Prompt: `"Add a REST endpoint for user authentication with JWT"`

  Expected terminal summary:
  ```
  Routed to:
  - backend (high, score N≥3)

  Reason: matched "endpoint", "authentication", "JWT".
  ```
  No "Also relevant" block.

  Expected task JSON: `routing_decision.selected_teams` has backend with `confidence: "high"`. `secondary_teams` and `filtered_teams` populated. `status: "pending"`.

- [ ] **Case 2 — High + secondary**

  Prompt: `"Build a SaaS platform with user requirements and API endpoints"`

  Expected terminal summary:
  ```
  Routed to:
  - backend (high, score N≥3)

  Also relevant (not dispatched):
  - product (medium, score 1–2)

  Reason: matched "API", "SaaS", ...
  ```

  Expected task JSON: `selected_teams` = backend, `secondary_teams` = product.

- [ ] **Case 3 — Medium-only fallback**

  Prompt: `"Help me think about a feature for my product"`

  Expected: routes to product (medium), no "Also relevant". Summary says "No high-confidence teams found."

  Expected task JSON: `selected_teams` has product with `confidence: "medium"`. `secondary_teams: []`.

- [ ] **Case 4 — Full fallback / needs clarification**

  Prompt: `"Help me with this thing"`

  Expected: no team dispatched, task JSON has `status: "needs_clarification"`, `selected_teams: []`. Terminal shows exactly one clarifying question.

- [ ] **Case 5 — Negative keyword suppression**

  Prompt: `"Write a blog post about our iOS app and its features"`

  Background: In `.claude/routing.json`, the market rule has `"iOS"` in its `negative_keywords`. So even though "blog post" matches market's positives (+1), "iOS" fires the -2 penalty → market net_score = -1 → filtered.

  Expected: no high-confidence team survives. Fallback fires. Task JSON has `status: "needs_clarification"`, `selected_teams: []`, and `filtered_teams` includes market with `matched_negative: ["iOS"]`. Terminal shows exactly one clarifying question.

- [ ] **Final commit (tag)**

  ```bash
  git tag v0.2.0
  git push origin main --tags
  ```

  Update `VERSION` file if present:
  ```bash
  echo "0.2.0" > VERSION
  git add VERSION
  git commit -m "chore: bump version to 0.2.0"
  ```
