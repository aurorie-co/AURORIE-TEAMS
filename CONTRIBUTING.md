# Contributing

We're building the AI company OS — and we're opinionated about it. We value coherence over volume.

## Rules

**1. Open an issue first.**
Before writing any code or adding new concepts, open an issue to discuss the direction. PRs without prior alignment may be closed.

**2. Follow existing naming conventions.**
- Team names: lowercase kebab (`backend`, `frontend`, `product`)
- Artifact files: lowercase kebab (`prd.md`, `backend-implementation.md`)
- Agent names: `aurorie-<team>-<role>.md`
- Routing fields: `positive_keywords`, `negative_keywords`, `example_requests` (v2 schema)

**3. Respect the directory structure.**
- `teams/<team>/` — team source files (workflow, agents, skills, mcp)
- `shared/` — routing and skills shared across teams
- `.claude/` — installed output (do not edit directly in PRs)
- `tests/` — test suites

**4. Do not introduce overlapping concepts.**
Before adding a new team or skill, verify it doesn't overlap with an existing one. The system is designed to be coherent, not comprehensive.

**5. Run tests before opening a PR.**

```bash
bash tests/install.test.sh && bash tests/lint.test.sh
```

All tests must pass. Routing, workflows, and agent files must be consistent.
