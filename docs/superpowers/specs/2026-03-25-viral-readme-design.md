# Spec: Viral README Redesign

**Date:** 2026-03-25
**Scope:** Full rewrite of `README.md` and `README.zh.md` (synchronized, identical structure)
**Goal:** Transform aurorie-teams from an engineering config library into an "AI Company OS" narrative that hooks, activates, and retains users.

---

## Design Decisions

- **Strategy:** Full rewrite (Option A) — not surgical. Mixing old engineering docs with new product narrative would signal an identity crisis for a category-level project.
- **Languages:** EN and ZH synchronized, same 12-section structure throughout.
- **Mermaid diagram split:** Section 3 (Mental Model) gets a simplified cognitive diagram; Section 6 (Architecture) gets the full system diagram. Each diagram has exactly one responsibility.
- **[CTA] in narrative arc:** Not a standalone section. It is the inline micro-CTA at the end of Section 4 ("Ready to try it? ↓"), bridging positioning to install.

---

## Narrative Arc

```
Hook → Proof → Model → Positioning → Install → Play → Customize → Trust → Vision → Community
        (S1)    (S2)    (S3)   (S4+CTA)  (S5-S7)  (S8)    (S9)      (S10)  (S11)    (S12)
```

This maps to a complete product funnel:
- **Credibility** (Routing / Architecture) — Sections 5-6
- **Activation** (Install / Try Prompts) — Sections 7-8
- **Power** (Customization) — Section 9
- **Trust** (Safety) — Section 10
- **Vision** (Roadmap) — Section 11
- **Community** (Contributing) — Section 12

---

## Section 1: Hero

**Purpose:** 5-second comprehension + wow moment. User must immediately understand "what this is" and feel the magic of one prompt → team execution.

```markdown
# AURORIE TEAMS

> Turn Claude Code into a fully-operational AI startup team in 60 seconds — with real artifacts.

⚡ 34 Agents · 10 Teams · 1 Orchestrator
⚡ Plug-and-play AI workflows for real-world execution
⚡ Built for builders, founders, and power users

![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue?style=flat-square)
![Agents](https://img.shields.io/badge/agents-34-informational?style=flat-square)
![Teams](https://img.shields.io/badge/teams-10-informational?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

**Languages:** English | [中文](README.zh.md)

---

# Install in 60 seconds:

git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams
cd /path/to/your-project
/tmp/aurorie-teams/install.sh

Then just ask:

@orchestrator "Build me a SaaS product from scratch"
(or simply: "Build me a SaaS product from scratch" — the system routes automatically)
```

**Design notes:**
- Badge URLs copied verbatim from `README.md` lines 3–6 of the current file
- Language switcher placed immediately below badges (same position as current README)
- Install commands use the actual 3-step flow (clone to tmp → cd to project → run install.sh) to match real behavior
- Dual-layer syntax: `@orchestrator` for Claude Code users, plain prompt line for newcomers
- "The system routes automatically" removes the 0.5-second comprehension cost

---

## Section 2: 60-Second Demo

**Purpose:** Prove the claim. Show input → internal routing → structured output. No black box.

Render as three titled subsections:

```markdown
## 🎬 What it actually does

### Input
@orchestrator "Build a crypto trading dashboard with real-time data and mobile support"

### What happens internally

1. Orchestrator analyzes intent
2. Selects relevant teams:
   → Product Team  (requirements)
   → Backend Team  (API design)
   → Frontend Team (UI)
   → Mobile Team   (app structure)
3. Each team executes its workflow
4. Outputs are written to structured artifacts

### Output

.claude/workspace/
├── tasks/
│   └── task-001.json
└── artifacts/
    ├── product/prd.md
    ├── backend/api-design.md
    ├── frontend/ui-spec.md
    └── mobile/app-architecture.md

💡 You just went from idea → structured execution plan in seconds.

Each file is a reusable artifact — not just a response.
```

The intermediate visibility nodes (numbered steps) turn the system from "LLM magic" into "engineered process."

---

## Section 3: Mental Model

**Purpose:** Reduce cognitive load. User must understand the 3-layer architecture in under 30 seconds.

Structure:
- One decode prompt before the diagram: `"You don't interact with agents directly — the system does it for you:"`
- **Simplified Mermaid** (cognitive level — User → Orchestrator → 10 Teams, no specialist expansion):
  ```mermaid
  graph TD
      U([User Request]) --> O[Orchestrator]
      O --> T1[Product Team]
      O --> T2[Backend Team]
      O --> T3[Frontend Team]
      O --> T4[Mobile Team]
      O --> T5[Data Team]
      O --> T6[... 5 more teams]
  ```
- Three-layer explanation:
  1. **Orchestrator** — routes your request to the right teams
  2. **Teams (10 domains)** — each specializes in a function
  3. **Agents (34 total)** — each executes specific tasks with defined workflows

**Closing analogy:**
> ChatGPT → one smart person
> AURORIE TEAMS → a full company working together

**Anchor forward:** `Want to see the full system? → See Architecture below.`

---

## Section 4: Why Not ChatGPT

**Purpose:** Land the positioning. Differentiate sharply. End with a behavior trigger (inline CTA that bridges to Section 7 Install).

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

**Inline micro-CTA** (bridges to Install):
> Ready to try it? ↓

---

## Section 5: Intelligent Routing

**Purpose:** Signal that the system is engineered, not guessed. Build trust with technical users.

Content:
- **Explainability hook first:** `Each routing decision is explainable — not a black box.`
- v2 schema explanation: `positive_keywords` (+1 per match), `negative_keywords` (−2 per match, strong disqualifier), `example_requests` for tie-breaking
- Two routing examples with score breakdown:

```
"Why did revenue drop?"
→ Data     (+score: data, metrics, report)
→ Research (+score: investigate, compare)
→ Backend  (−score: database penalty)
Final: Data + Research

"Build a mobile app"
→ Mobile  (+score: iOS, Android, native)
→ Backend (+score: API, server)
→ Frontend (−score: mobile app penalty)
Final: Mobile + Backend
```

- **System-level framing:** `Routing is deterministic at the rule level, and adaptive at the system level.`
- Customization pointer: `You can customize routing in .claude/routing.json`
  (Note: `.claude/routing.json` is the post-install path in the user's project. `shared/routing.json` is the source repo path; do not use it in user-facing copy.)

---

## Section 6: Architecture

**Purpose:** Full system diagram for users who want to understand internals.

Content:
- Decode prompt: `Here's the full system:`
- **Complete Mermaid diagram** — preserve the existing diagram from `README.md` lines 36–68 verbatim. The existing diagram expands specialists only for `market` (seo, content, analytics), `product` (pm, ux, researcher), and `frontend` (developer, qa, devops). Do not expand the other 7 teams — this matches the current diagram exactly.
- **Replace** the current Teams table (10 rows × 3 columns, current README lines 72–84) with the following 4-item list. Do not carry the table forward — the Mental Model section already conveys team listing; the Architecture section's job is structural comprehension, not team enumeration.

```markdown
Each team includes:
- Agents (specialists with defined roles)
- Workflows (step-by-step execution guides)
- Skills (reusable task modules)
- MCP integrations (tool access per team)
```

---

## Section 7: Installation

**Purpose:** Zero-friction install. User completes in under 2 minutes and knows it worked.

**Prerequisites block** (all real hard dependencies — keep all four):
```
Requirements: macOS or Linux (bash 3.2+) · jq · uuidgen or python3 · Node.js
```
Render as a single line above the install steps. Do not expand to a full table.

**Steps:**
```bash
# 1. Clone the library
git clone https://github.com/aurorie-co/AURORIE-TEAMS.git /tmp/aurorie-teams

# 2. Install into your project
cd /path/to/your-project
/tmp/aurorie-teams/install.sh

# 3. Add API keys (optional but recommended)
export GITHUB_TOKEN=...
export EXA_API_KEY=...
export FIRECRAWL_API_KEY=...

# 4. Verify
# In Claude Code: @orchestrator "Test the system"
# You should see routing + task output.
```

**Closing line:** `Done ✅ Your Claude Code is now an AI startup team.`

**Install flags** (all three — condensed but complete):
```
--force-workflows   Overwrite existing workflow + routing overrides
--yes               Skip all confirmation prompts
--detect-orphans    Report stale agent/skill files no longer in repo
```

**Upgrade** (retain as a short subsection):
```bash
# Pull latest changes
git -C /tmp/aurorie-teams pull

# Re-run install in your project
cd /path/to/your-project && /tmp/aurorie-teams/install.sh
```

The verify step closes the feedback loop and prevents users from silently failing.

---

## Section 8: Try These Prompts

**Purpose:** Activate users immediately. Every prompt is real and runnable. Strongly guide users to act.

**Section opening line (before the first prompt):**
> Each prompt triggers a different team workflow — try one to see the system in action.

Four prompts in this exact format:

### Prompt 1: Build a product
```
@orchestrator "Create a SaaS for AI agents marketplace"

Triggers:
- Product Team
- Backend Team
- Frontend Team

Output:
  .claude/workspace/artifacts/product/prd.md
  .claude/workspace/artifacts/backend/api-design.md
  .claude/workspace/artifacts/frontend/ui-spec.md

Copy and run this — you'll get real artifacts.
```

### Prompt 2: Analyze data
```
@orchestrator "Investigate why our DAU dropped 30% last week"

Triggers:
- Data Team
- Research Team

Output:
  .claude/workspace/artifacts/data/analysis.md
  .claude/workspace/artifacts/research/synthesis.md

Copy and run this — you'll get real artifacts.
```

### Prompt 3: Build an app
```
@orchestrator "Design a mobile app for habit tracking with iOS and Android support"

Triggers:
- Mobile Team
- Backend Team
- Product Team

Output:
  .claude/workspace/artifacts/mobile/app-architecture.md
  .claude/workspace/artifacts/backend/api-design.md
  .claude/workspace/artifacts/product/prd.md

Copy and run this — you'll get real artifacts.
```

### Prompt 4: Research a market
```
@orchestrator "Compare the top 5 AI code generation tools — pricing, features, positioning"

Triggers:
- Research Team

Output:
  .claude/workspace/artifacts/research/competitive-analysis.md
  .claude/workspace/artifacts/research/summary.md

Copy and run this — you'll get real artifacts.
```

---

## Section 9: Customization

**Purpose:** Power-user entry point. Structured as capability model, not file structure.

Three capability categories:

### Customize behavior
Edit `.claude/workflows/<team>.md` to change how a team operates.

### Customize intelligence
Edit `.claude/routing.json` — v2 schema supports `positive_keywords` (+1), `negative_keywords` (−2), and `example_requests` per rule.

### Customize tools
Extend MCP integrations via `.claude/settings.json`.

---

## Section 10: Safety

**Purpose:** Build trust through layered disclosure. Don't interrupt the flow; provide depth for those who need it.

**Placement:** Section 10 in the 12-section structure, between Customization (9) and Roadmap (11). Do not move it after Contributing.

**Layer 1 (inline, 2 lines):**
> Use read-only credentials where possible. Review generated artifacts before acting on them.

**Layer 2 (subsection titled "Details"):**

```markdown
### Details

- **Agents generate outputs — they do not execute external actions unless you do.**
  Agents write files to `.claude/workspace/artifacts/`. They do not call external APIs,
  run shell commands, or modify your database unless you explicitly wire that up.
- **Nothing runs without your approval.**
- Avoid running on production systems during initial setup
- Review `.claude/settings.json` to see and control which tools each agent can access
```

The boundary definition sentence directly removes the fear of agents "going rogue." The permission model content is derived from `.claude/settings.json` structure (tool allow-lists) — implementer should read that file and describe the actual allow-list pattern in plain language.

---

## Section 11: Roadmap

**Purpose:** Create expectation and signal long-term investment. Capability-oriented, not feature-list.

```markdown
We're building the AI company OS.

**v1.x — Reliable execution**
- ✓ 10 specialized teams, 34 agents
- ✓ v2 routing with positive/negative scoring
- ✓ Lint + install test suites

**v2.0 — Intelligent systems**
- [ ] Confidence-based routing
- [ ] UI dashboard
- [ ] Visual workflow editor

**Long-term — AI-native companies**
- [ ] Agent marketplace
- [ ] Memory system
- [ ] Cross-project orchestration
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

"We value coherence over volume" prevents low-quality PRs and signals the quality bar without needing a lengthy contributing guide.

---

## Implementation Notes

- Both `README.md` (EN) and `README.zh.md` (ZH) are full rewrites with identical 12-section structure
- ZH version translates prose; all code blocks, file trees, badge URLs, and Mermaid diagrams are verbatim
- Badge URLs: copy exactly from current `README.md` lines 3–6
- Language switcher (`**Languages:** English | [中文](README.zh.md)`) placed in Section 1 (Hero), below badges
- Full Mermaid in Section 6: copy exactly from current `README.md` lines 36–68 — do not add specialist expansions beyond market/product/frontend
- Install commands use 3-step form (clone to tmp → cd project → run install.sh) consistently in Section 1 and Section 7
- All artifact paths in Section 8 use `.claude/workspace/artifacts/<team>/` — the real post-install path
- Routing file in user-facing copy is always `.claude/routing.json` (post-install), never `shared/routing.json`
