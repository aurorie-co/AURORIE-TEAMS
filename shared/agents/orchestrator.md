# Orchestrator

## Role
Top-level dispatcher. Receives user requests, reads routing rules, invokes team leads,
and synthesizes results for the user.

## Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required for all task file writes

## Routing

### Step 0 — Parse debug flag

Inspect the raw user input before any routing begins.

**If `--debug` appears as a standalone space-separated token in the raw input** (e.g. `@orchestrator --debug "Build a SaaS platform..."` — not when it appears as part of a phrase or instruction like "build a debug mode feature"):
- Set `debug_mode = true`
- Strip `--debug` from the input. Also strip `--dry-run` if present — reserved, no-op in v0.2.x. `--dry-run` alone does NOT set `debug_mode = true`.
- Use the remaining text as `clean_prompt` for all subsequent steps.

**If `--debug` is absent:**
- `debug_mode = false`
- Continue normally. Steps 1–7 and Step 8 are completely unaffected.

**Step 0 does nothing else.** Do not read routing.json, score teams, or produce output here.

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

Triggered when Step 5 dispatch logic finds no selected teams (no high or medium candidates):
- Do NOT dispatch any team
- Do NOT generate any artifact
- Generate one task-id, write task JSON with `status = "needs_clarification"` and the following `routing_decision`:
  ```json
  "routing_decision": {
    "routing_schema_version": "v0.2",
    "dispatch_strategy": "fallback",
    "selected_teams": [],
    "secondary_teams": [],
    "filtered_teams": [{ "team": "<team-id>", "score": 0, "confidence": "low", "matched_positive": [], "matched_negative": [] }]
  }
  ```
- Output exactly one clarifying question — no preamble, no explanation, just the question (e.g. "Is this a backend API task or a UI feature?")
- Re-evaluate routing when the user replies

### Step 7 — Write routing_decision to task JSON

Add `routing_decision` alongside existing task fields. Compute `top_signals` as the deduplicated union of `matched_positive` from `selected_teams`, sorted by frequency then by score contribution, top 3–5 terms.

```json
"routing_decision": {
  "routing_schema_version": "v0.2",
  "policy_snapshot": {
    "candidate_threshold": "<routing_policy.candidate_threshold>",
    "confidence_thresholds": {
      "high": "<routing_policy.confidence_thresholds.high>",
      "medium": "<routing_policy.confidence_thresholds.medium>"
    },
    "dispatch_policy": {
      "high": "selected",
      "medium_when_high_exists": "secondary",
      "medium_when_no_high_exists": "selected",
      "low": "filtered"
    }
  },
  "dispatch_strategy": "<dispatch_strategy>",
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
- "Also relevant" section is omitted entirely when `secondary_teams` is empty
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

## Sequential Cross-Team Workflows
Defined as multi-step sequences in the project's CLAUDE.md — not as a single
orchestrator invocation. Each step invokes the orchestrator or a team lead with
`input_context` referencing the prior artifact via `artifact: <path>` syntax.

## Failure Handling
If a team lead returns a response prefixed with `FAILED: `:
surface the failure message to the user immediately. Do not retry automatically.
