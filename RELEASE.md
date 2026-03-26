# v0.3.0 — Dispatch Policy: Programmable Decision Engine

**Not a routing system. A decision engine with observability and guarantees.**

---

## What changed

v0.3 adds a `dispatch_policy` layer to the orchestrator. For the first time, you control what happens per confidence band after classification:

```json
"dispatch_policy": {
  "high": "auto",          // dispatch immediately
  "medium": {
    "when_high_exists": "ignore",   // surface only
    "when_no_high_exists": "ask"   // confirm first
  }
}
```

Three actions per band:
- **`auto`** — dispatch without asking
- **`ask`** — show a Y/n prompt before dispatching medium teams
- **`ignore`** — suppress the team entirely

### Ask mode

When `ask` is triggered:

```
Medium-confidence teams identified:
- product (score 2)
- frontend (score 1)
Dispatch these teams? [Y/n]
```

- `y` / `yes` / `<empty>` → dispatch
- `n` / `no` → suppress
- Invalid input → re-prompt once → then treat as `no`

Ask fires at most once per routing invocation. All medium teams requiring ask are grouped into a single prompt.

---

## What this unlocks

The orchestrator now maintains a full `routing_decision` after every invocation:

```json
{
  "routing_schema_version": "v0.3",
  "selected_teams": [...],
  "secondary_teams": [...],
  "ignored_teams": [...],
  "ask_resolution": {
    "triggered": true,
    "context": "medium_when_no_high_exists",
    "teams": ["product"],
    "user_response": "yes"
  }
}
```

This makes the system:
- **Programmable** — policy-driven, not hardcoded
- **Observable** — every decision is recorded
- **Testable** — 73 tests covering the full state machine
- **Explainable** — `--debug` shows the full trace

---

## Architecture

The key architectural split is clean:

```
Step 5  → "What is the world?" (classification — facts)
Step 5.5 → "What do I choose?" (policy — decision)
Step A/B → "Just execute." (execution — no knowledge of policy)
```

Secondary teams and ignored teams are never dispatched — they are informational only.

---

## Tests

73 tests, all green:
- 50 lint checks (source tree contract)
- 5 routing regression cases
- 18 dispatch policy cases (normalize, auto/ignore, ask mode, dry-run)

---

## Migration

Default `dispatch_policy` reproduces v0.2 behavior exactly. No action required unless you want to customize.

```bash
python3 tests/routing/test_dispatch_policy.py
python3 tests/routing/test_routing_cases.py
bash tests/lint.test.sh
```

Full spec: `docs/specs/2026-03-26-dispatch-policy-design.md`
