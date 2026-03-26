# Changelog

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
