# Spec: Viral README Redesign

**Date:** 2026-03-25
**Scope:** Full rewrite of `README.md` and `README.zh.md` (synchronized, identical structure)
**Goal:** Transform aurorie-teams from an engineering config library into an "AI Company OS" narrative that hooks, activates, and retains users.

---

## Design Decisions

- **Strategy:** Full rewrite (Option A) — not surgical. Mixing old engineering docs with new product narrative would signal an identity crisis for a category-level project.
- **Languages:** EN and ZH synchronized, same 12-section structure throughout.
- **Mermaid diagram split:** Section 3 (Mental Model) gets a simplified cognitive diagram; Section 6 (Architecture) gets the full system diagram. Each diagram has exactly one responsibility.

---

## Narrative Arc

```
Hook → Proof → Model → Positioning → [CTA] → Install → Play → Customize → Trust → Vision → Community
```

This maps to a complete product funnel:
- **Credibility** (Routing / Architecture)
- **Activation** (Install / Try Prompts)
- **Power** (Customization)
- **Trust** (Safety)
- **Vision** (Roadmap)
- **Community** (Contributing)

---

## Section 1: Hero

**Purpose:** 5-second comprehension + wow moment. User must immediately understand "what this is" and feel the magic of one prompt → team execution.

```markdown
# AURORIE TEAMS

> Turn Claude Code into a fully-operational AI startup team in 60 seconds.

⚡ 34 Agents · 10 Teams · 1 Orchestrator
⚡ Plug-and-play AI workflows for real-world execution
⚡ Built for builders, founders, and power users

[badges: platform / agents / teams / license]

git clone https://github.com/aurorie-co/AURORIE-TEAMS.git
cd AURORIE-TEAMS && ./install.sh

Then just ask:

@orchestrator "Build me a SaaS product from scratch"
(or simply: "Build me a SaaS product from scratch" — the system routes automatically)
```

**Design notes:**
- Dual-layer syntax: `@orchestrator` for Claude Code users, plain prompt for newcomers
- "The system routes automatically" removes the 0.5-second comprehension cost
- Badge row preserved as visual anchor on GitHub

---

## Section 2: 60-Second Demo

**Purpose:** Prove the claim. Show input → internal routing → structured output. No black box.

Structure:
1. **Input** — one natural language prompt
2. **What happens internally** — numbered routing steps showing orchestrator analyzing intent, selecting teams, executing workflows
3. **Output** — real file tree (`artifacts/product/prd.md`, `artifacts/backend/api-design.md`, `artifacts/frontend/ui-spec.md`, `artifacts/mobile/app-architecture.md`)
4. **Closing line:** `💡 You just went from idea → structured execution plan in one prompt.`
5. **Artifact framing:** `Each file is a reusable artifact — not just a response.`

The intermediate visibility nodes (numbered steps) are critical: they turn the system from "LLM magic" into "engineered process."

---

## Section 3: Mental Model

**Purpose:** Reduce cognitive load. User must understand the 3-layer architecture in under 30 seconds.

Structure:
- One decode prompt before the diagram: `"You don't interact with agents directly — the system does it for you:"`
- **Simplified Mermaid** (cognitive level only): User → Orchestrator → Teams (no specialist expansion)
- Three-layer explanation:
  1. Orchestrator: routes your request to the right teams
  2. Teams (10 domains): each specializes in a function
  3. Agents (34 total): each executes specific tasks

**Closing analogy:**
> ChatGPT → single brain
> AURORIE TEAMS → full company

---

## Section 4: Why Not ChatGPT

**Purpose:** Land the positioning. Differentiate sharply. End with a behavior trigger.

Comparison table:

| ChatGPT | AURORIE TEAMS |
|---------|---------------|
| One response | Multi-step execution |
| Generalist | Specialized teams |
| Ephemeral output | Structured artifacts |
| Manual thinking | Automated orchestration |

**Closing copy:**
> You don't need one answer.
> You need a team that executes.

**Micro CTA:**
> Ready to try it? ↓

---

## Section 5: Intelligent Routing

**Purpose:** Signal that the system is engineered, not guessed. Build trust with technical users.

Content:
- v2 schema explanation: `positive_keywords` (+1 per match), `negative_keywords` (−2 per match, strong disqualifier), `example_requests` for tie-breaking
- Two routing examples with score breakdown:
  ```
  "Why did revenue drop?"
  → Data    (+score: data, metrics, report)
  → Research (+score: investigate, compare)
  → Backend (−score: database penalty)
  Final: Data + Research
  ```
- **Explainability hook:** `Each routing decision is explainable — not a black box.`
- Customization pointer: `Edit shared/routing.json`

---

## Section 6: Architecture

**Purpose:** Full system diagram for users who want to understand internals.

Content:
- Decode prompt: `Here's the full system:`
- **Complete Mermaid diagram** (existing diagram, all 10 teams + specialist expansion for market/product/frontend)
- Below diagram: each team includes Agents / Workflows / Skills / MCP integrations

---

## Section 7: Installation

**Purpose:** Zero-friction install. User completes in under 2 minutes and knows it worked.

Steps:
1. Clone
2. `./install.sh`
3. Add API keys (`GITHUB_TOKEN`, `EXA_API_KEY`, `FIRECRAWL_API_KEY`)
4. **Verify:** `@orchestrator "Hello"` → you should see routing + task output

**Closing line:** `Done ✅ Your Claude Code is now an AI startup team.`

The verify step is critical: it closes the feedback loop and prevents users from silently failing.

---

## Section 8: Try These Prompts

**Purpose:** Activate users immediately. Every prompt is real and runnable.

Four prompts, each with:
- The prompt (copy-ready)
- Triggered teams (standardized format)
- Expected output file tree

Format:
```markdown
### Build a product
@orchestrator "Create a SaaS for AI agents marketplace"

Triggers:
- Product Team
- Backend Team
- Frontend Team

Output:
  artifacts/product/prd.md
  artifacts/backend/api-design.md
  artifacts/frontend/ui-spec.md

Copy and run this — you'll get real artifacts.
```

Four prompts: Build a product / Analyze data / Build an app / Research a market.

---

## Section 9: Customization

**Purpose:** Power-user entry point. Structured as capability model, not file structure.

Three capability categories:

### Customize behavior
Edit `.claude/workflows/<team>.md` to change how a team operates.

### Customize intelligence
Edit `shared/routing.json` — v2 schema supports `positive_keywords`, `negative_keywords`, `example_requests` per team rule.

### Customize tools
Extend MCP integrations via `.claude/settings.json`.

---

## Section 10: Safety

**Purpose:** Build trust through layered disclosure. Don't interrupt the flow; provide depth for those who need it.

**Layer 1 (inline, 2 lines):**
> Use read-only credentials where possible. Review generated artifacts before acting on them.

**Layer 2 (subsection):**
- Agents generate outputs — they do not execute external actions unless you do.
- Avoid running on production systems
- Permission model explanation (what agents can read/write)

The boundary definition sentence (`Agents generate outputs — they do not execute external actions unless you do.`) directly removes the fear of agents "going rogue."

---

## Section 11: Roadmap

**Purpose:** Create expectation and signal long-term investment. Capability-oriented, not feature-oriented.

```
We're building the AI company OS.

v1.x — Reliable execution
  ✓ 10 teams, 34 agents
  ✓ v2 routing with positive/negative scoring
  ✓ Lint + install test suites

v2.0 — Intelligent systems
  □ Confidence-based routing
  □ UI dashboard
  □ Visual workflow editor

Long-term — AI-native companies
  □ Agent marketplace
  □ Memory system
  □ Cross-project orchestration
```

---

## Section 12: Contributing

**Purpose:** Open posture, but you control quality and direction.

```markdown
We're building the AI company OS — and we're opinionated about it.

Want to help?
- Add new teams
- Improve routing logic
- Build workflows
- Share use cases

We value coherence over volume.

Open a PR 🚀
```

"We value coherence over volume" prevents low-quality PRs and signals quality bar without needing a lengthy contributing guide.

---

## Implementation Notes

- Both `README.md` (EN) and `README.zh.md` (ZH) are full rewrites with identical section structure
- ZH version translates content, preserving all code blocks and file trees verbatim
- Existing Mermaid diagram is reused in Section 6 (full version); Section 3 gets a new simplified version
- All file tree examples must use real paths that exist after install (verify against actual artifact structure)
- Badge URLs preserved from current README
