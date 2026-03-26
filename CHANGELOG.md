# Changelog

## 0.6.0 — 2026-03-26

### Added

#### Replay Interface
- `@orchestrator --replay <task-id>` — read-only inspection of past task execution
- `format_replay_output(task)` — pure function producing structured replay output
- `reconstruct_waves(nodes)` — pure function reconstructing wave order from `depends_on` depth
- Handles old task JSONs gracefully: missing `waves`, `started_at`, `completed_at` display as `—`
- Output includes: prompt, status, routing (selected/secondary/ignored), wave timeline, final status, milestone ref

#### Resume Interface
- `@orchestrator --resume <task-id>` — continue DAG execution from partial state
- `validate_resume(task)` — pure function enforcing strict state priority:
  - `pending_decision` present → NOT resumable (must `--resolve` first)
  - `execution_graph` absent → no graph found
  - `execution_graph.status = completed` → already done
  - `execution_graph.status = pending` → nothing to resume
  - `execution_graph.status = user_declined_dispatch` → declined
- **Resume from `in_progress`**: Step C dispatch loop from current state
- **Resume from `partial_failed`**: `reset_partial_failed_graph(graph)` — only `failed` nodes reset to `pending`; done/blocked/running untouched
- **Resume from `blocked`**: `unblock_graph(graph, artifact_map)` — re-checks `artifacts_in` before unblocking; only nodes with all artifacts present are unblocked
- Human-in-the-loop: partial_failed and blocked paths prompt for confirmation before mutating state
- After terminal state reached: writes updated task JSON + milestone re-aggregation if milestone attached

#### State Priority Invariant
- Critical invariant codified: `pending_decision` presence always blocks resume
- `pending_decision` is a human decision marker — never bypassed by `--resume`
- `task.status` is derived/secondary; `execution_graph.status` is the control signal

### Changed

- Orchestrator Step 0 extended with `--replay <task-id>` and `--resume <task-id>` flag parsing
- `shared/agents/orchestrator.md` and `.claude/agents/orchestrator.md` kept in sync

### Test Coverage
- 17 new replay/resume tests: 5 replay + 7 resume validation + 2 reconstruct_waves + 1 reset_partial_failed_graph + 2 unblock_graph
- Combined with v0.5 suites: **100/100 tests green**

### Planned
- `--resume --force` — skip confirmation prompt for automated recovery (P2)
- Graph visualization — visual display of execution graph and wave progression (v0.7)
- Automatic retry — retry failed nodes without user confirmation (v0.7)
- Cross-task resume — resume all tasks in a milestone at once (v0.8)

---

## 0.5.0 — 2026-03-26

### Added

#### Milestone Coordination
- Introduce milestone as a persistent, cross-task coordination layer
- Aggregate task states into milestone-level progress (pending / in_progress / completed / partial_failed)
- Support milestone-scoped task grouping and tracking
- Milestone does NOT influence routing decisions (v0.5 constraint)
- Tasks can be added to a milestone, but not removed (append-only constraint)
- Schema: `.claude/workspace/milestones/<milestone-id>.json` with `milestone_id`, `title`, `status`, `tasks[]`, `created_at`, `updated_at`
- Task JSON embeds lightweight `milestone` ref: `{milestone_id, title}`
- CLI: `--milestone "<title>" "<prompt>"` creates milestone and attaches task
- CLI: `--milestone-status <milestone-id>` queries and displays aggregated status
- Pure functions: `create_milestone`, `attach_task_to_milestone`, `aggregate_milestone_status`, `get_milestone_ref`
- 83/83 tests passing (16 unit + 2 E2E wiring + 65 prior dispatch/routing/graph/milestone)

#### Selective Interactive Routing
- Extend resolve interface: `all | none | selective`
- CLI: `@orchestrator --resolve <task-id> selective <team1,team2,...>`
- `pending_decision.options` extends to `["all", "none", "selective"]`
- User picks which medium teams to approve — partial dispatch
- `resolve_task()` handles selective: confirmed → selected_teams (or secondary when high exists), unconfirmed → ignored_teams
- Empty selective list → same as `none` (declined_after_ask set)
- Invalid team-ids in selective list → silently ignored (no error)
- Idempotent: same selective payload resolved twice → same result

### Planned

#### DAG Dry-Run
- Add execution graph preview mode
- Display wave order and dependencies without dispatch

---

## 0.4.0 — 2026-03-26

### Added
- `pending_decision` schema — replaces `ask_required: true` boolean with full structured payload: `type`, `band`, `context`, `teams[]`, `options[]`, `default`
- `awaiting_dispatch_decision` task status — parks task when ask is triggered; distinct from `needs_clarification` (system uncertain) and `user_declined_dispatch` (declined after ask)
- Resolve interface — `--resolve <task-id> all|none`: applies user decision to recompute selected/ignored, clears pending_decision, resumes via Step C
- `--resolve` CLI flag parsed in Step 0; idempotent resolution
- Debug trace updated — shows `pending_decision` block (band, context, teams, options, default)
- v0.4 routing summary — when parked, shows medium teams with confirm/decline CLI instructions
- `execution_graph` schema in routing_decision — nodes with depends_on, artifact handoff paths, status per node
- Step C — DAG dispatch loop: wave-based execution, parallel dispatch of ready nodes, partial failure handling
- Full spec: `docs/specs/2026-03-26-v0.4-interactive-routing-and-dag-design.md`

### Changed
- `routing_schema_version` bumped to `"v0.4"` in routing_decision
- `ask_required` removed — replaced by `pending_decision`
- `ask_resolution` removed — replaced by resolve interface
- Step 5.5 ask now parks task (sets `pending_decision` + `awaiting_dispatch_decision`) and stops; no longer proceeds to Steps A/B
- v0.3 backward compatibility: tasks with `ask_required: true` (no `pending_decision`) are read-equivalent to `pending_decision` with `options: ["all", "none"]`, `default: "none"`

### Phase 1 complete (interactive routing contract)
- pending_decision schema
- awaiting_dispatch_decision status
- resolve interface (all-or-none, v0.4-a)

### Phase 2 complete (DAG execution)
- select_graph_template: strict priority (data-first > research-branch > linear-pipeline > flat-parallel)
- build_execution_graph: builds nodes + edges per template, artifact_in/out paths
- get_ready_nodes: depends_on all done → ready to dispatch
- advance_node: pure status transitions, graph status updates (pending → in_progress → completed/partial_failed)
- Step C: DAG dispatch loop — wave-based parallel dispatch, blocked node handling

---

## 0.3.1 — 2026-03-26

### Added
- `--dry-run` flag — compute routing decision without dispatching teams
- `ask_required` in `routing_decision` — deferred ask marker for dry-run mode
- 5 dry-run test cases — total dispatch policy suite now 18 cases (normalize 4, auto/ignore 4, ask 5, dry-run 5)
- `--dry-run` section in README.md with example output
- `.claude/agents/orchestrator.md` synced with shared Step 0 flag parsing

### Changed
- orchestrator.md Step 0 — `--dry-run` parsed as standalone flag, sets `dry_run_mode = true`
- orchestrator.md Step 5.5 — ask defers to `ask_required` dict when `dry_run_mode = true`
- orchestrator.md Step 6 — `ask_required` included in fallback `routing_decision`
- orchestrator.md Step 7.5 — debug trace shows `dry_run: true` line when applicable
- orchestrator.md Step 8 — dry-run appends "Dry run — no teams were dispatched." and ask deferral note
- orchestrator.md Steps A/B — skipped entirely when `dry_run_mode = true`
- Tests paragraph updated — 73 total (50 lint + 5 routing + 18 dispatch)
- RELEASE.md — test counts updated to 73 / 18

---

## 0.3.0 — 2026-03-26

### Added
- `dispatch_policy` in `routing.json` — per-confidence-band dispatch control (auto / ask / ignore)
- `normalize_dispatch_policy` — pure function, fills missing policy keys with v0.2-equivalent defaults
- `apply_dispatch_policy` — Step 5.5 enforcement: auto, ignore, and interactive ask mode
- Ask mode — Y/n confirmation prompt for medium-confidence teams, at most once per routing
- `secondary_teams[]` and `ignored_teams[]` in `routing_decision` — distinguish surfaced vs. suppressed teams
- `ask_resolution` in `routing_decision` — replay/audit record of user decisions
- Step 7.5 debug trace updated — shows dispatch_policy, ignored_teams, and ask_resolution
- 13-case dispatch policy test suite — normalize (4), auto/ignore (4), ask mode (5)
- `dispatch_policy` field in `--debug` output

### Changed
- Step 5 renamed "Classify candidates" — outputs `high_candidates[]` and `medium_candidates[]` (not dispatch set)
- Step 6 fallback now distinguishes `user_declined_dispatch` vs `needs_clarification`
- `routing_schema_version` bumped to `"v0.3"` in `routing_decision`
- Steps A/B constraint clarified — `secondary_teams` are informational only, never dispatched
- orchestrator.md (shared + .claude) fully updated to v0.3 step architecture

### Fixed
- Ask mode guard: prevents ask trigger when `medium_candidates` is empty

---

## 1.1.0 — 2026-03-25

### Added
- 10 teams (frontend, backend, infra, design added alongside existing 6)
- 34 agents total — full team specialization with lead + specialist structure
- `lint.test.sh` — 50-test source tree contract suite (agents/workflows/skills/routing)
- routing.json v2 schema: `positive_keywords` (+1), `negative_keywords` (−2), `example_requests` for tie-breaking
- Orchestrator updated to explain +1/−2 scoring and primary intent disambiguation

### Changed
- `README.md` and `README.zh.md` — full rewrite: viral narrative arc, 13 sections, synchronized EN/ZH
- `.gitignore` — now ignores `.claude/` (entire local config dir) and `CLAUDE.md`
- `CLAUDE.md` un-tracked from git; use `templates/CLAUDE.md.template` as source of truth

### Fixed
- `install.test.sh` routing version assertion updated from v1 to v2

---

## 1.0.0 — 2026-03-22

### Added
- Initial release
- Six teams: engineer, market, product, data, research, support
- install.sh with --force-workflows, --detect-orphans, --yes flags
- Shared orchestrator agent and file-handoff skill
- Machine-readable routing.json
- MCP secrets via shell env var references
