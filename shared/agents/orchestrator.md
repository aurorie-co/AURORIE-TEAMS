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

Normalize `dispatch_policy` (pure function — same input always produces same output):
- If `dispatch_policy` is absent or incomplete, fill missing keys with:
  - `high = "auto"`
  - `medium.when_high_exists = "ignore"`
  - `medium.when_no_high_exists = "auto"`
- These defaults reproduce v0.2 dispatch behavior exactly.

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

### Step 5 — Classify candidates

```
if any high candidates exist:
    high_candidates = all high candidates (sorted order)
    medium_candidates = all medium candidates
    dispatch_strategy = "conditional"

elif any medium candidates exist:
    high_candidates = []
    medium_candidates = all medium candidates (sorted order)
    dispatch_strategy = "conditional"

else:
    → FALLBACK (Step 6): status = "needs_clarification"
```

Step 5 produces classification only — it does not produce `selected_teams` or `secondary_teams`.
Step 5.5 applies `dispatch_policy` and produces the final dispatch set.

### Step 5.5 — Apply dispatch_policy

**Precondition:** `dispatch_policy` has been normalized in Step 1. `high_candidates[]` and `medium_candidates[]` are available from Step 5.

**Determine medium context:**
```
if high_candidates is non-empty → medium_context = "when_high_exists"
else                            → medium_context = "when_no_high_exists"
```

**Apply policy per band:**

```
HIGH candidates:
  action = dispatch_policy.high
  "auto"   → add to selected_teams
  "ignore" → add to ignored_teams

MEDIUM candidates:
  action = dispatch_policy.medium[medium_context]
  "auto":
    if medium_context = "when_no_high_exists" → add to selected_teams
    if medium_context = "when_high_exists"    → add to secondary_teams
  "ignore" → add to ignored_teams
  "ask"    → trigger ask mode (see below)
```

**Ask mode** (triggered when action = "ask"):
- Ask mode is triggered **at most once** per routing invocation. If multiple medium candidates require "ask", they are grouped into a single prompt.
- Ask mode applies only to the medium band. High teams and ignored teams are not affected.

Output:
```
Medium-confidence teams identified:
- <team> (score N)
- <team> (score N)
Dispatch these teams? [Y/n]
```

Input contract:
- `y` / `yes` / `<empty>` → dispatch all prompted teams (same as `auto` for this context); `user_response = "yes"`
- `n` / `no` → add all to `ignored_teams`; `user_response = "no"`
- invalid → re-prompt once: `"Please reply y or n."`
- invalid (second time) → treat as `no`; `user_response = "default_no"`

**Outputs of Step 5.5:**
- `selected_teams[]` — teams that will be dispatched
- `secondary_teams[]` — medium teams surfaced for context but not dispatched (when_high_exists + auto action only). Never dispatched in Steps A/B — informational only.
- `ignored_teams[]` — teams suppressed by policy (ignore action) or user decision (ask → no/default_no)
- `ask_resolution` — present only when ask was triggered; omit otherwise

**ask_resolution schema:**
```json
{
  "triggered": true,
  "context": "medium_when_no_high_exists",
  "teams": ["product", "frontend"],
  "user_response": "yes"
}
```

**Semantic boundary:**
- `secondary_teams` and `ignored_teams` are mutually exclusive.
- `secondary_teams` = surfaced for context, not dispatched.
- `ignored_teams` = explicitly suppressed by policy or user decision.

**Trigger Step 6 (Fallback) if `selected_teams` is empty after this step.**

When `selected_teams` contains multiple teams, dispatch them in parallel (Step B).
When `selected_teams` contains one team, use single dispatch (Step A).

### Step 6 — Fallback

Triggered when no teams remain selected after Step 5.5 policy enforcement. Two cases:

- **`user_declined_dispatch`**: ask mode was triggered AND `user_response` is `"no"` or `"default_no"`.
- **`needs_clarification`**: `selected_teams` is empty AND no ask was triggered (e.g., all candidates filtered or ignored by policy).

In both cases:
- Do NOT dispatch any team
- Do NOT generate any artifact
- Generate one task-id, write task JSON with the appropriate `status` and the following `routing_decision`:
  ```json
  "routing_decision": {
    "routing_schema_version": "v0.3",
    "dispatch_strategy": "fallback",
    "selected_teams": [],
    "secondary_teams": [],
    "ignored_teams": [],
    "filtered_teams": [{ "team": "<team-id>", "score": 0, "confidence": "low", "matched_positive": [], "matched_negative": [] }]
  }
  ```
- Output exactly one clarifying question — no preamble, no explanation, just the question (e.g. "Is this a backend API task or a UI feature?")
- Re-evaluate routing when the user replies

### Step 7 — Write routing_decision to task JSON

Add `routing_decision` alongside existing task fields. Compute `top_signals` as the deduplicated union of `matched_positive` from `selected_teams`, sorted by frequency then by score contribution, top 3–5 terms.

```json
"routing_decision": {
  "routing_schema_version": "v0.3",
  "policy_snapshot": {
    "candidate_threshold": "<routing_policy.candidate_threshold>",
    "confidence_thresholds": {
      "high": "<routing_policy.confidence_thresholds.high>",
      "medium": "<routing_policy.confidence_thresholds.medium>"
    },
    "dispatch_policy": {
      "high": "<routing_policy.dispatch_policy.high>",
      "medium": {
        "when_high_exists": "<routing_policy.dispatch_policy.medium.when_high_exists>",
        "when_no_high_exists": "<routing_policy.dispatch_policy.medium.when_no_high_exists>"
      }
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
  "ignored_teams": [
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
  ],
  "ask_resolution": {
    "triggered": true,
    "context": "<medium_when_high_exists|medium_when_no_high_exists>",
    "teams": ["<team-id>"],
    "user_response": "<yes|no|default_no>"
  }
}
```

Note: `ask_resolution` is omitted from the task JSON when ask was not triggered.
`ignored_teams` is present and may be empty when no teams were suppressed.

Always use the actual `routing_policy` values from the current `routing.json` when writing `policy_snapshot` — not hardcoded values.

### Step 7.5 — Render debug trace (debug mode only)

**Skip entirely if `debug_mode = false`.**

**Precondition:** Step 7 has written `routing_decision` to the task JSON.

Read the following fields from `routing_decision`. Do not re-evaluate or re-score anything — all values come from `routing_decision` as already written in Step 7.

Fields needed:
- `dispatch_strategy` — top-level field on `routing_decision`
- `policy_snapshot.candidate_threshold`
- `policy_snapshot.confidence_thresholds.high`
- `policy_snapshot.confidence_thresholds.medium`
- `policy_snapshot.dispatch_policy.high`
- `policy_snapshot.dispatch_policy.medium.when_high_exists`
- `policy_snapshot.dispatch_policy.medium.when_no_high_exists`
- `selected_teams[]` — each entry: `team`, `score`, `confidence`, `matched_positive[]`, `matched_negative[]`
- `secondary_teams[]` — same fields
- `ignored_teams[]` — same fields
- `filtered_teams[]` — same fields
- `ask_resolution` — present only when ask was triggered

Print exactly this block:

```
=== ROUTING DEBUG ===

Policy:
- candidate_threshold: <policy_snapshot.candidate_threshold>
- confidence.high: <policy_snapshot.confidence_thresholds.high>
- confidence.medium: <policy_snapshot.confidence_thresholds.medium>
- dispatch_policy.high: <policy_snapshot.dispatch_policy.high>
- dispatch_policy.medium.when_high_exists: <policy_snapshot.dispatch_policy.medium.when_high_exists>
- dispatch_policy.medium.when_no_high_exists: <policy_snapshot.dispatch_policy.medium.when_no_high_exists>
- dispatch_strategy: <routing_decision.dispatch_strategy>

Evaluations:
<for each team: first selected_teams entries, then secondary_teams, then ignored_teams, then filtered_teams>
<team>: score <score>, <confidence> → <state>
  + <matched_positive joined by ", ", or "(none)" if empty>
  - <matched_negative joined by ", ", or "(none)" if empty>

Dispatch:
  Selected:  <selected_teams[*].team joined by ", ", or "(none)" if empty>
  Secondary: <secondary_teams[*].team joined by ", ", or "(none)" if empty>
  Ignored:  <ignored_teams[*].team joined by ", ", or "(none)" if empty>
  Filtered:  <filtered_teams[*].team joined by ", ", or "(none)" if empty>
<if ask_resolution is present:
Ask:
  Context: <ask_resolution.context>
  User said: <ask_resolution.user_response>
  Teams prompted: <ask_resolution.teams[*].team joined by ", ">
}
=== END ROUTING DEBUG ===
```

Rendering rules:
- `score`: read from `routing_decision` only — never recomputed. If the field is absent, display `N/A`.
- `confidence = low`: assigned when score < `confidence_thresholds.medium` (implicit — not a configurable key in `routing_policy`).
- `state`: `selected` for entries in `selected_teams`, `secondary` for `secondary_teams`, `ignored` for `ignored_teams`, `filtered` for `filtered_teams`.
- Within each group (selected → secondary → ignored → filtered), maintain the order from `routing_decision` (score desc, positive_count desc, negative_count asc — matching Step 3.5 sort order).
- All four Dispatch lines (Selected / Secondary / Ignored / Filtered) are always printed, even when empty (show `(none)`).
- Ask block is printed only when `ask_resolution` is present in `routing_decision`.
- Fallback case: `Selected: (none)`, `Secondary: (none)`, all teams appear under `Filtered`.

Proceed immediately to Step 8 after printing.

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

**Constraint:** Dispatch `selected_teams` only. `secondary_teams` are informational and must never be dispatched here.

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

**Constraint:** Dispatch `selected_teams` only. `secondary_teams` are informational and must never be dispatched here.

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
