#!/usr/bin/env bash
set -euo pipefail

PASS=0; FAIL=0
# Note: use (( VAR += 1 )) not (( VAR++ )) — post-increment returns old value,
# which is exit code 1 when VAR was 0, causing set -e to abort.
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [[ "$expected" == "$actual" ]]; then
    echo "  ✓ $desc"; (( PASS += 1 ))
  else
    echo "  ✗ $desc" >&2
    echo "    expected: '$expected'" >&2
    echo "    got:      '$actual'" >&2
    (( FAIL += 1 ))
  fi
}

assert_file_exists() {
  local desc="$1" path="$2"
  if [[ -e "$path" ]]; then
    echo "  ✓ $desc"; (( PASS += 1 ))
  else
    echo "  ✗ $desc (missing: $path)" >&2; (( FAIL += 1 ))
  fi
}

assert_file_absent() {
  local desc="$1" path="$2"
  if [[ ! -e "$path" ]]; then
    echo "  ✓ $desc"; (( PASS += 1 ))
  else
    echo "  ✗ $desc (should not exist: $path)" >&2; (( FAIL += 1 ))
  fi
}

assert_file_contains() {
  local desc="$1" path="$2" pattern="$3"
  if grep -qF "$pattern" "$path" 2>/dev/null; then
    echo "  ✓ $desc"; (( PASS += 1 ))
  else
    echo "  ✗ $desc (pattern '$pattern' not found in $path)" >&2; (( FAIL += 1 ))
  fi
}

# ── setup temp project ────────────────────────────────────────────────────────
TMPDIR_PROJECT="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_PROJECT"' EXIT
cd "$TMPDIR_PROJECT"
touch .gitignore

echo ""
echo "=== Test: default install ==="
"$REPO_ROOT/install.sh" > /dev/null

assert_file_exists "orchestrator.md installed"      ".claude/agents/orchestrator.md"
assert_file_exists "aurorie-backend-lead.md installed"      ".claude/agents/aurorie-backend-lead.md"
assert_file_exists "aurorie-frontend-lead.md installed"     ".claude/agents/aurorie-frontend-lead.md"
assert_file_exists "aurorie-mobile-lead.md installed"       ".claude/agents/aurorie-mobile-lead.md"
assert_file_exists "tdd skill installed"            ".claude/skills/tdd/SKILL.md"
assert_file_exists "file-handoff skill installed"   ".claude/skills/file-handoff/SKILL.md"
assert_file_exists "backend workflow installed"     ".claude/workflows/backend.md"
assert_file_exists "mobile workflow installed"      ".claude/workflows/mobile.md"
assert_file_exists "routing.json installed"         ".claude/routing.json"
assert_file_exists "settings.json generated"        ".claude/settings.json"
assert_file_exists "CLAUDE.md generated"            "CLAUDE.md"
assert_file_exists ".aurorie-teams-version written" ".claude/.aurorie-teams-version"
assert_file_contains ".gitignore has workspace entry" ".gitignore" ".claude/workspace/"
assert_file_contains "github MCP in settings.json"  ".claude/settings.json" '"github"'
assert_file_contains "exa MCP in settings.json"     ".claude/settings.json" '"exa"'
assert_file_contains "firecrawl MCP in settings.json"  ".claude/settings.json" '"firecrawl"'
assert_file_contains "puppeteer MCP in settings.json"  ".claude/settings.json" '"puppeteer"'
assert_file_contains "playwright MCP in settings.json" ".claude/settings.json" '"playwright"'
assert_file_contains "postgres MCP in settings.json" ".claude/settings.json" '"postgres"'
assert_file_contains "sqlite MCP in settings.json"   ".claude/settings.json" '"sqlite"'

echo ""
echo "=== Test: routing.json skipped on second install ==="
echo '{"version":"custom"}' > .claude/routing.json
"$REPO_ROOT/install.sh" > /dev/null
routing_version="$(cat .claude/routing.json)"
assert_eq "custom routing.json preserved" '{"version":"custom"}' "$routing_version"

echo ""
echo "=== Test: --force-workflows --yes overwrites routing.json ==="
"$REPO_ROOT/install.sh" --force-workflows --yes > /dev/null 2>&1
routing_v="$(jq -r '.version' .claude/routing.json)"
assert_eq "routing.json reset to repo version" "1" "$routing_v"

echo ""
echo "=== Test: workflow skipped if exists ==="
echo "custom workflow" > .claude/workflows/engineer.md
"$REPO_ROOT/install.sh" > /dev/null
assert_file_contains "custom workflow preserved" ".claude/workflows/engineer.md" "custom workflow"

echo ""
echo "=== Test: CLAUDE.md skipped if exists ==="
echo "custom content" > CLAUDE.md
"$REPO_ROOT/install.sh" > /dev/null
assert_file_contains "existing CLAUDE.md preserved" "CLAUDE.md" "custom content"

echo ""
echo "=== Test: settings.json has mcpServers ==="
mcp_count="$(jq -r '.mcpServers | keys | length' .claude/settings.json)"
assert_eq "settings.json has MCP entries" "true" "$([[ "$mcp_count" -ge 1 ]] && echo true || echo false)"

echo ""
echo "=== Test: settings.json preserves locally-added MCP server ==="
jq '.mcpServers["local-custom"] = {"command":"custom","args":[]}' .claude/settings.json > .claude/settings.json.tmp
mv .claude/settings.json.tmp .claude/settings.json
"$REPO_ROOT/install.sh" > /dev/null
has_local="$(jq -r '.mcpServers | has("local-custom")' .claude/settings.json)"
assert_eq "locally-added MCP server preserved after reinstall" "true" "$has_local"

echo ""
echo "=== Test: version file matches repo VERSION ==="
installed_version="$(cat .claude/.aurorie-teams-version)"
repo_version="$(cat "$REPO_ROOT/VERSION")"
assert_eq ".aurorie-teams-version matches repo VERSION" "$repo_version" "$installed_version"

echo ""
echo "=== Test: .gitignore not duplicated on second install ==="
"$REPO_ROOT/install.sh" > /dev/null
count="$(grep -c ".claude/workspace/" .gitignore)"
assert_eq ".gitignore entry not duplicated" "1" "$count"

echo ""
echo "=== Test: --force-workflows without --yes aborts in non-TTY ==="
echo "custom-again" > .claude/routing.json
"$REPO_ROOT/install.sh" --force-workflows < /dev/null > /dev/null 2>&1 || true
still_custom="$(cat .claude/routing.json)"
assert_eq "--force-workflows without --yes aborts (non-TTY)" "custom-again" "$still_custom"

echo ""
echo "=== Test: --detect-orphans reports stale agent ==="
echo "stub" > .claude/agents/old-legacy-agent.md
output="$("$REPO_ROOT/install.sh" --detect-orphans 2>&1)"
assert_eq "--detect-orphans reports orphaned agent" "true" \
  "$([[ "$output" == *"old-legacy-agent.md"* ]] && echo true || echo false)"

echo ""
echo "=== Test: postgres key collision warning emitted ==="
collision_output="$("$REPO_ROOT/install.sh" 2>&1)"
assert_eq "install warns on postgres key collision" "true" \
  "$([[ "$collision_output" == *"postgres"* ]] && echo true || echo false)"

echo ""
echo "=== Results ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
