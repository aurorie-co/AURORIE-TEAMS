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

echo ""
echo "=== Routing: run deterministic routing test suite ==="
python3 "$(dirname "$0")/routing/test_routing_cases.py"
ROUTING_EXIT=$?

[[ $FAIL -eq 0 && $ROUTING_EXIT -eq 0 ]] && exit 0 || exit 1
