# P1 — Weighted Routing + Lint/Contract Tests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `routing.json` from a flat keyword list to a schema with positive keywords, negative keywords, and example requests; update the orchestrator to use the new schema. Add a `tests/lint.test.sh` that validates structural consistency across agents, workflows, skills, and routing.

**Architecture:** The routing schema gains `positive_keywords`, `negative_keywords`, and `example_requests` per rule. `negative_keywords` let the orchestrator demote a match when disqualifying signals are present. The orchestrator agent prompt is updated to explain how to apply positive/negative scoring. The lint test is a standalone bash script that runs without installing to a temp project — it validates the source tree directly.

**Tech Stack:** JSON, bash, markdown

---

## File Map

| File | Action | What changes |
|------|--------|-------------|
| `shared/routing.json` | Modify | Upgrade to v2 schema: add `positive_keywords`, `negative_keywords`, `example_requests`; bump `version` to `"2"` |
| `shared/agents/orchestrator.md` | Modify | Update routing instructions to explain positive/negative scoring and `primary_intent` disambiguation |
| `tests/install.test.sh` | Modify | Update `routing.json` version assertion from `"1"` to `"2"` |
| `tests/lint.test.sh` | Create | New contract test: validates agents, workflows, skills, routing consistency |

---

### Task 1: Upgrade `shared/routing.json` to v2 schema

**Files:**
- Modify: `shared/routing.json`

- [ ] **Step 1: Read the current file**

  Read `shared/routing.json` and note all 10 team rules.

- [ ] **Step 2: Write the v2 schema**

  Replace the entire file with the following. The key changes per rule:
  - `keywords` renamed to `positive_keywords`
  - `negative_keywords` added (signals that demote this team's match)
  - `example_requests` added (3 canonical examples per team)
  - `version` bumped to `"2"`

  ```json
  {
    "version": "2",
    "rules": [
      {
        "team": "backend",
        "description": "Server-side API, database, auth, and backend service tasks",
        "positive_keywords": ["backend", "API", "endpoint", "REST", "GraphQL", "server", "database", "schema", "migration", "authentication", "authorization", "JWT", "session", "background job", "queue", "worker", "ORM", "SQL", "bug fix"],
        "negative_keywords": ["mobile app", "iOS", "Android", "React component", "Vue", "CSS", "Terraform", "IaC", "design token", "brand"],
        "example_requests": [
          "Add a REST endpoint for user authentication with JWT",
          "Write a database migration to add a soft-delete column",
          "Fix the background job that processes webhook payloads"
        ]
      },
      {
        "team": "frontend",
        "description": "Web UI components, styles, and client-side logic tasks",
        "positive_keywords": ["frontend", "UI", "component", "React", "Vue", "CSS", "layout", "web page", "browser", "accessibility", "responsive", "client-side", "bundle", "web app"],
        "negative_keywords": ["iOS", "Android", "Swift", "Kotlin", "backend API", "database", "Terraform", "brand identity"],
        "example_requests": [
          "Build a responsive navigation component in React",
          "Fix the CSS layout bug on the dashboard page",
          "Add keyboard accessibility to the modal component"
        ]
      },
      {
        "team": "mobile",
        "description": "Native iOS and Android app development tasks",
        "positive_keywords": ["mobile", "iOS", "Android", "Swift", "Kotlin", "SwiftUI", "Jetpack", "Compose", "Xcode", "Gradle", "TestFlight", "Play Store", "native"],
        "negative_keywords": ["web app", "React", "Vue", "CSS", "backend API", "database migration", "Terraform"],
        "example_requests": [
          "Add dark mode support to the iOS SwiftUI app",
          "Fix the Android Compose navigation back-stack bug",
          "Submit the new build to TestFlight for beta testing"
        ]
      },
      {
        "team": "market",
        "description": "Marketing, content, and growth tasks",
        "positive_keywords": ["marketing", "SEO", "content", "social", "campaign", "blog", "copywriting", "analytics", "growth", "acquisition", "landing page", "ad copy"],
        "negative_keywords": ["database", "API", "code", "backend", "frontend component", "iOS", "Android", "Terraform", "data pipeline"],
        "example_requests": [
          "Write a blog post announcing our new API for developer audiences",
          "Run an SEO audit on our pricing page and suggest improvements",
          "Draft a landing page for the new mobile SDK targeting iOS developers"
        ]
      },
      {
        "team": "product",
        "description": "Product definition, requirements, and UX tasks",
        "positive_keywords": ["product", "feature", "PRD", "requirements", "roadmap", "UX", "user story", "wireframe", "specification", "user flow", "persona"],
        "negative_keywords": ["implement", "code", "deploy", "database migration", "CSS", "iOS", "Android", "Terraform", "SEO audit"],
        "example_requests": [
          "Write a PRD for a dark mode feature across all platforms",
          "Define user stories for the onboarding flow redesign",
          "Create a UX brief for the new dashboard with user flow diagrams"
        ]
      },
      {
        "team": "data",
        "description": "Data analysis, reporting, pipeline tasks, and data quality investigations",
        "positive_keywords": ["data", "report", "dashboard", "metrics", "pipeline", "ETL", "analysis", "chart", "query", "insight", "discrepancy", "anomaly", "numbers look wrong", "data quality", "root cause"],
        "negative_keywords": ["marketing campaign", "blog post", "iOS", "Android", "React component", "Terraform", "API endpoint", "brand"],
        "example_requests": [
          "Build a weekly retention cohort report from the events table",
          "Investigate why DAU dropped 30% last Thursday",
          "Fix the ETL pipeline that ingests Stripe webhook events"
        ]
      },
      {
        "team": "research",
        "description": "Research, synthesis, and information gathering tasks",
        "positive_keywords": ["research", "compare", "summarize", "market research", "competitor", "survey", "synthesis", "landscape", "benchmark", "evaluate options"],
        "negative_keywords": ["implement", "build", "deploy", "fix bug", "database", "code review", "iOS", "Android"],
        "example_requests": [
          "Research the top AI code generation tools and compare pricing and features",
          "Summarize user sentiment about our checkout flow from recent reviews",
          "Do a competitor analysis of auth providers for our SSO decision"
        ]
      },
      {
        "team": "support",
        "description": "Customer support and issue response tasks",
        "positive_keywords": ["support", "customer", "ticket", "complaint", "help", "response", "escalate", "refund", "user reported", "customer said"],
        "negative_keywords": ["code", "implement", "deploy", "database", "Terraform", "SEO", "PRD", "roadmap"],
        "example_requests": [
          "Draft a response to a Pro customer whose data export returned an empty file",
          "Triage this support ticket and assess priority: user cannot log in after password reset",
          "Escalate this billing dispute — customer claims they were charged twice"
        ]
      },
      {
        "team": "infra",
        "description": "Cloud infrastructure as code (Terraform), IaC review, and audit tasks",
        "positive_keywords": ["infrastructure", "terraform", "IaC", "provision", "cloud", "VPC", "IAM", "S3", "EC2", "RDS", "ECS", "EKS", "Kubernetes", "load balancer", "IaC review", "terraform audit"],
        "negative_keywords": ["React", "iOS", "Android", "blog post", "PRD", "database query", "data pipeline", "support ticket"],
        "example_requests": [
          "Write a Terraform module to provision an ECS cluster with autoscaling",
          "Review the IAM policies in the staging environment for least-privilege violations",
          "Audit the VPC configuration for our new AWS region rollout"
        ]
      },
      {
        "team": "design",
        "description": "Design system (tokens, component specs, accessibility) and brand identity tasks",
        "positive_keywords": ["design system", "design token", "token", "component spec", "brand", "brand guide", "logo", "visual identity", "typography", "color palette", "spacing", "WCAG", "accessibility audit", "brand consistency", "design review", "marketing asset"],
        "negative_keywords": ["implement in React", "backend", "database", "Terraform", "data pipeline", "SEO", "support ticket"],
        "example_requests": [
          "Define the spacing and typography tokens for the new design system",
          "Run a WCAG 2.1 AA accessibility audit on the component library",
          "Create brand guidelines for the new product sub-brand"
        ]
      }
    ],
    "fallback": "orchestrator-clarify"
  }
  ```

- [ ] **Step 3: Validate JSON is well-formed**

  ```bash
  jq . shared/routing.json > /dev/null && echo "valid JSON"
  ```
  Expected: `valid JSON`

- [ ] **Step 4: Commit**

  ```bash
  git add shared/routing.json
  git commit -m "feat(routing): upgrade to v2 schema with positive/negative keywords and example requests"
  ```

---

### Task 2: Update `shared/agents/orchestrator.md` routing instructions

**Files:**
- Modify: `shared/agents/orchestrator.md`

- [ ] **Step 1: Read the current file**

  Read `shared/agents/orchestrator.md` and note the Routing section.

- [ ] **Step 2: Update the Routing section**

  Replace the current Routing section with the following:

  ```markdown
  ## Routing

  1. Read `.claude/routing.json`.
  2. For each rule, score the user request:
     - **+1** for each `positive_keywords` match (case-insensitive, partial word match counts)
     - **−2** for each `negative_keywords` match (strong disqualifier)
     - A rule is a **candidate** if its net score ≥ 1 after negatives
  3. Use `example_requests` to break ties: if two teams have equal scores, pick the one whose examples most closely match the request's intent.
  4. If one candidate: single dispatch (Step A).
  5. If multiple candidates with similar scores: parallel dispatch (Step B).
  6. If no candidates (`fallback: "orchestrator-clarify"`): ask the user one clarifying question, then re-evaluate.

  **Disambiguation rule:** When a request mixes signals (e.g., "investigate why our React component is slow"), identify the *primary intent* (performance investigation → data/research) vs. *secondary intent* (React → frontend) and route to the primary intent team only.
  ```

- [ ] **Step 3: Commit**

  ```bash
  git add shared/agents/orchestrator.md
  git commit -m "feat(routing): update orchestrator to use positive/negative scoring with primary intent disambiguation"
  ```

---

### Task 3: Update install test for v2 routing schema

**Files:**
- Modify: `tests/install.test.sh`

- [ ] **Step 1: Find the version assertion**

  Locate the test:
  ```bash
  routing_v="$(jq -r '.version' .claude/routing.json)"
  assert_eq "routing.json reset to repo version" "1" "$routing_v"
  ```

- [ ] **Step 2: Update expected value to "2"**

  ```bash
  assert_eq "routing.json reset to repo version" "2" "$routing_v"
  ```

- [ ] **Step 3: Run install tests**

  ```bash
  bash tests/install.test.sh
  ```
  Expected: `Failed: 0`

- [ ] **Step 4: Commit**

  ```bash
  git add tests/install.test.sh
  git commit -m "test: update routing version assertion to v2"
  ```

---

### Task 4: Create `tests/lint.test.sh`

**Files:**
- Create: `tests/lint.test.sh`

The lint test validates source tree consistency without doing a full install. It checks:
1. Every team in `routing.json` has a `teams/<team>/` directory
2. Every team has a `workflow.md` and at least one agent file
3. Every team has a `mcp.json`
4. The lead agent for each team is named `aurorie-<team>-lead.md`
5. No user-facing files reference `engineer-lead`
6. Every skill referenced in agent files exists as a directory in `shared/skills/` or `teams/*/skills/`

- [ ] **Step 1: Write the test file**

  Create `tests/lint.test.sh`:

  ```bash
  #!/usr/bin/env bash
  set -euo pipefail

  PASS=0; FAIL=0
  REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

  assert_ok() {
    local desc="$1"
    if eval "$2" &>/dev/null; then
      echo "  ✓ $desc"; (( PASS += 1 ))
    else
      echo "  ✗ $desc" >&2; (( FAIL += 1 ))
    fi
  }

  assert_fail() {
    local desc="$1"
    if ! eval "$2" &>/dev/null; then
      echo "  ✓ $desc"; (( PASS += 1 ))
    else
      echo "  ✗ $desc (expected no match but found one)" >&2; (( FAIL += 1 ))
    fi
  }

  TEAMS=$(jq -r '.rules[].team' "$REPO_ROOT/shared/routing.json")

  echo ""
  echo "=== Lint: routing.json teams have source directories ==="
  for team in $TEAMS; do
    assert_ok "teams/$team/ exists" "test -d '$REPO_ROOT/teams/$team'"
  done

  echo ""
  echo "=== Lint: each team has workflow.md ==="
  for team in $TEAMS; do
    assert_ok "teams/$team/workflow.md exists" "test -f '$REPO_ROOT/teams/$team/workflow.md'"
  done

  echo ""
  echo "=== Lint: each team has mcp.json ==="
  for team in $TEAMS; do
    assert_ok "teams/$team/mcp.json exists" "test -f '$REPO_ROOT/teams/$team/mcp.json'"
  done

  echo ""
  echo "=== Lint: each team has aurorie-<team>-lead.md agent ==="
  for team in $TEAMS; do
    assert_ok "teams/$team/agents/aurorie-$team-lead.md exists" \
      "test -f '$REPO_ROOT/teams/$team/agents/aurorie-$team-lead.md'"
  done

  echo ""
  echo "=== Lint: no stale engineer-lead references in user-facing files ==="
  assert_fail "no engineer-lead in templates/" \
    "grep -rl 'engineer-lead' '$REPO_ROOT/templates/'"
  assert_fail "no engineer-lead in README.md" \
    "grep -q 'engineer-lead' '$REPO_ROOT/README.md'"
  assert_fail "no engineer-lead in README.zh.md" \
    "grep -q 'engineer-lead' '$REPO_ROOT/README.zh.md'"

  echo ""
  echo "=== Lint: routing.json is valid JSON with required fields ==="
  assert_ok "routing.json is valid JSON" \
    "jq . '$REPO_ROOT/shared/routing.json'"
  assert_ok "routing.json has version field" \
    "jq -e '.version' '$REPO_ROOT/shared/routing.json'"
  assert_ok "routing.json has fallback field" \
    "jq -e '.fallback' '$REPO_ROOT/shared/routing.json'"
  assert_ok "all rules have positive_keywords" \
    "jq -e '[.rules[] | select(.positive_keywords == null)] | length == 0' '$REPO_ROOT/shared/routing.json'"
  assert_ok "all rules have negative_keywords" \
    "jq -e '[.rules[] | select(.negative_keywords == null)] | length == 0' '$REPO_ROOT/shared/routing.json'"
  assert_ok "all rules have example_requests" \
    "jq -e '[.rules[] | select(.example_requests == null)] | length == 0' '$REPO_ROOT/shared/routing.json'"

  echo ""
  echo "=== Lint: skills referenced in agent files exist ==="
  # Collect all available skill directories
  available_skills=()
  for s in "$REPO_ROOT/shared/skills/"*/; do
    [[ -d "$s" ]] && available_skills+=("$(basename "$s")")
  done
  for team in $TEAMS; do
    for s in "$REPO_ROOT/teams/$team/skills/"*/; do
      [[ -d "$s" ]] && available_skills+=("$(basename "$s")")
    done
  done

  # Check each agent file for skill references (lines matching "- <skill-name>:")
  skill_errors=0
  while IFS= read -r agent_file; do
    while IFS= read -r line; do
      # Match lines like: - skill-name: path
      if [[ "$line" =~ ^-\ ([a-z][a-z0-9-]+):\ .+ ]]; then
        skill_name="${BASH_REMATCH[1]}"
        found=false
        for s in "${available_skills[@]}"; do
          [[ "$s" == "$skill_name" ]] && found=true && break
        done
        if [[ "$found" == false ]]; then
          echo "  ✗ skill '$skill_name' referenced in $(basename "$agent_file") not found" >&2
          (( skill_errors += 1 )); (( FAIL += 1 ))
        fi
      fi
    done < "$agent_file"
  done < <(find "$REPO_ROOT/teams" "$REPO_ROOT/shared/agents" -name "*.md" -type f)

  [[ $skill_errors -eq 0 ]] && echo "  ✓ all skill references resolve" && (( PASS += 1 ))

  echo ""
  echo "=== Results ==="
  echo "  Passed: $PASS"
  echo "  Failed: $FAIL"
  [[ $FAIL -eq 0 ]] && exit 0 || exit 1
  ```

- [ ] **Step 2: Make executable and run**

  ```bash
  chmod +x tests/lint.test.sh
  bash tests/lint.test.sh
  ```
  Expected: `Failed: 0`

- [ ] **Step 3: Commit**

  ```bash
  git add tests/lint.test.sh
  git commit -m "test: add lint.test.sh — contract tests for agents, workflows, skills, routing consistency"
  ```

---

### Task 5: Wire lint into CI / README

**Files:**
- Modify: `README.md`
- Modify: `README.zh.md`

- [ ] **Step 1: Add a "Running tests" note to README**

  In the existing "How it works" or "Customizing" section, add a brief "Tests" subsection:

  ```markdown
  ## Tests

  Two test suites live in `tests/`:

  | Script | What it tests |
  |--------|--------------|
  | `tests/install.test.sh` | Full install lifecycle: file placement, routing preservation, MCP merge, orphan detection |
  | `tests/lint.test.sh` | Source tree consistency: agent/workflow/skill/routing contract validation |

  Run both with:
  ```bash
  bash tests/install.test.sh && bash tests/lint.test.sh
  ```
  ```

- [ ] **Step 2: Mirror in README.zh.md**

- [ ] **Step 3: Commit and push**

  ```bash
  git add README.md README.zh.md
  git commit -m "docs: add Tests section documenting install and lint test suites"
  git push origin main
  ```
