# Changelog

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
