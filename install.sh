#!/usr/bin/env bash
set -euo pipefail

# ── resolve paths ────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET="$PWD/.claude"
REPO_VERSION="$(cat "$REPO_ROOT/VERSION")"
INSTALLED_VERSION_FILE="$TARGET/.aurorie-teams-version"
FORCE_WORKFLOWS=false
DETECT_ORPHANS=false
YES=false

# ── parse flags ───────────────────────────────────────────────────────────────
for arg in "$@"; do
  case $arg in
    --force-workflows) FORCE_WORKFLOWS=true ;;
    --detect-orphans)  DETECT_ORPHANS=true ;;
    --yes)             YES=true ;;
  esac
done

# ── check dependencies ────────────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is required. Install with: brew install jq  or  apt install jq" >&2
  exit 1
fi

# ── print version transition ─────────────────────────────────────────────────
if [[ -f "$INSTALLED_VERSION_FILE" ]]; then
  PREV_VERSION="$(cat "$INSTALLED_VERSION_FILE")"
  if [[ "$PREV_VERSION" != "$REPO_VERSION" ]]; then
    echo "Updating aurorie-teams: $PREV_VERSION → $REPO_VERSION"
    echo "See $REPO_ROOT/CHANGELOG.md for what changed."
  else
    echo "Installing aurorie-teams $REPO_VERSION"
  fi
else
  echo "Installing aurorie-teams $REPO_VERSION"
fi

# ── create target directories ────────────────────────────────────────────────
mkdir -p "$TARGET/agents" "$TARGET/skills" "$TARGET/workflows" \
         "$TARGET/workspace/tasks" "$TARGET/workspace/artifacts"

# ── install agents (always overwrite) ────────────────────────────────────────
cp "$REPO_ROOT/shared/agents/orchestrator.md" "$TARGET/agents/"
for team in engineer market product data research support; do
  for agent_file in "$REPO_ROOT/teams/$team/agents/"*.md; do
    cp "$agent_file" "$TARGET/agents/"
  done
done
echo "  ✓ agents installed"

# ── install skills (always overwrite) ────────────────────────────────────────
cp -r "$REPO_ROOT/shared/skills/"* "$TARGET/skills/"
for team in engineer market product data research support; do
  cp -r "$REPO_ROOT/teams/$team/skills/"* "$TARGET/skills/"
done
echo "  ✓ skills installed"

# ── collect workflow + routing files that exist locally ───────────────────────
OVERWRITE_CANDIDATES=()
if [[ "$FORCE_WORKFLOWS" == true ]]; then
  for team in engineer market product data research support; do
    dest="$TARGET/workflows/$team.md"
    [[ -f "$dest" ]] && OVERWRITE_CANDIDATES+=("$dest")
  done
  dest="$TARGET/routing.json"
  [[ -f "$dest" ]] && OVERWRITE_CANDIDATES+=("$dest")
fi

# ── confirm overwrite if needed ───────────────────────────────────────────────
if [[ ${#OVERWRITE_CANDIDATES[@]} -gt 0 ]]; then
  if [[ "$YES" == false ]]; then
    # Abort silently if stdin is not a TTY (non-interactive / CI without --yes)
    if [[ ! -t 0 ]]; then
      echo "ERROR: --force-workflows requires --yes in non-interactive mode." >&2
      exit 1
    fi
    echo ""
    echo "The following files exist locally and will be overwritten:"
    for f in "${OVERWRITE_CANDIDATES[@]}"; do echo "  $f"; done
    echo ""
    read -r -p "Overwrite these files? [y/N] " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
      echo "Aborted."
      exit 0
    fi
  fi
fi

# ── install workflows ─────────────────────────────────────────────────────────
for team in engineer market product data research support; do
  src="$REPO_ROOT/teams/$team/workflow.md"
  dest="$TARGET/workflows/$team.md"
  if [[ "$FORCE_WORKFLOWS" == true ]]; then
    cp "$src" "$dest"
    echo "  WARNING: overwriting $dest" >&2
  else
    # portable skip-if-exists (avoids cp -n portability issues)
    [[ -f "$dest" ]] || cp "$src" "$dest"
  fi
done
echo "  ✓ workflows installed (existing local overrides preserved)"

# ── install routing.json ──────────────────────────────────────────────────────
routing_dest="$TARGET/routing.json"
if [[ "$FORCE_WORKFLOWS" == true ]]; then
  cp "$REPO_ROOT/shared/routing.json" "$routing_dest"
  echo "  WARNING: overwriting $routing_dest" >&2
else
  [[ -f "$routing_dest" ]] || cp "$REPO_ROOT/shared/routing.json" "$routing_dest"
fi
echo "  ✓ routing.json installed"

# ── merge mcp configs into settings.json ─────────────────────────────────────
settings_dest="$TARGET/settings.json"
merged_mcp="{}"

# collect all mcp.json paths: shared first, then teams alphabetically (hardcoded for safety)
mcp_files=("$REPO_ROOT/shared/mcp.json")
for team in engineer market product data research support; do
  mcp_file="$REPO_ROOT/teams/$team/mcp.json"
  [[ -f "$mcp_file" ]] && mcp_files+=("$mcp_file")
done

for mcp_file in "${mcp_files[@]}"; do
  incoming="$(jq '.mcpServers // {}' "$mcp_file")"
  # check for key collisions
  collisions="$(jq -rn \
    --argjson a "$merged_mcp" \
    --argjson b "$incoming" \
    '($a | keys) as $ak | ($b | keys) as $bk | $ak - ($ak - $bk) | .[]' 2>/dev/null || true)"
  if [[ -n "$collisions" ]]; then
    echo "WARNING: MCP server key collision in $mcp_file: $collisions (last definition wins)" >&2
  fi
  merged_mcp="$(jq -s '.[0] * .[1]' <(echo "$merged_mcp") <(echo "$incoming"))"
done

if [[ -f "$settings_dest" ]]; then
  # validate existing settings.json
  if ! jq . "$settings_dest" &>/dev/null; then
    echo "WARNING: existing settings.json is malformed — backing up to settings.json.bak" >&2
    cp "$settings_dest" "${settings_dest}.bak"
    echo "{}" > "$settings_dest"
  fi
  # merge: preserve all non-mcpServers keys; locally-added entries kept, repo entries overwrite matching keys
  existing_mcp="$(jq '.mcpServers // {}' "$settings_dest")"
  # existing_mcp first, then merged_mcp overwrites matching keys
  final_mcp="$(jq -s '.[0] * .[1]' <(echo "$existing_mcp") <(echo "$merged_mcp"))"
  jq --argjson mcp "$final_mcp" '. + {mcpServers: $mcp}' "$settings_dest" > "${settings_dest}.tmp"
  mv "${settings_dest}.tmp" "$settings_dest"
else
  jq -n --argjson mcp "$merged_mcp" '{mcpServers: $mcp}' > "$settings_dest"
fi
echo "  ✓ settings.json merged"

# ── generate CLAUDE.md if absent ─────────────────────────────────────────────
if [[ ! -f "CLAUDE.md" ]]; then
  cp "$REPO_ROOT/templates/CLAUDE.md.template" "CLAUDE.md"
  echo "  ✓ CLAUDE.md generated from template"
else
  echo "  - CLAUDE.md already exists, skipping"
fi

# ── append .gitignore block if not present ────────────────────────────────────
gitignore_marker=".claude/workspace/"
if [[ ! -f ".gitignore" ]] || ! grep -qF "$gitignore_marker" ".gitignore"; then
  { echo ""; cat "$REPO_ROOT/templates/.gitignore.template"; } >> ".gitignore"
  echo "  ✓ .gitignore updated"
else
  echo "  - .gitignore already contains workspace entry, skipping"
fi

# ── write installed version ───────────────────────────────────────────────────
echo "$REPO_VERSION" > "$INSTALLED_VERSION_FILE"
echo "  ✓ version recorded: $REPO_VERSION"

# ── detect orphans ────────────────────────────────────────────────────────────
if [[ "$DETECT_ORPHANS" == true ]]; then
  echo ""
  echo "Checking for orphaned files..."

  # build list of expected agent basenames
  repo_agents=("orchestrator.md")
  for team in engineer market product data research support; do
    for f in "$REPO_ROOT/teams/$team/agents/"*.md; do
      [[ -f "$f" ]] && repo_agents+=("$(basename "$f")")
    done
  done

  orphaned_agents=()
  for f in "$TARGET/agents/"*.md; do
    [[ -f "$f" ]] || continue
    name="$(basename "$f")"
    found=false
    for r in "${repo_agents[@]}"; do [[ "$r" == "$name" ]] && found=true && break; done
    [[ "$found" == false ]] && orphaned_agents+=("$f")
  done

  if [[ ${#orphaned_agents[@]} -gt 0 ]]; then
    echo "Orphaned agents (not in repo):"
    for f in "${orphaned_agents[@]}"; do echo "  $f"; done
  else
    echo "  No orphaned agents found."
  fi

  # build list of expected skill directory names
  repo_skills=()
  for s in "$REPO_ROOT/shared/skills/"*/; do
    [[ -d "$s" ]] && repo_skills+=("$(basename "$s")")
  done
  for team in engineer market product data research support; do
    for s in "$REPO_ROOT/teams/$team/skills/"*/; do
      [[ -d "$s" ]] && repo_skills+=("$(basename "$s")")
    done
  done

  orphaned_skills=()
  for d in "$TARGET/skills/"*/; do
    [[ -d "$d" ]] || continue
    name="$(basename "$d")"
    found=false
    for r in "${repo_skills[@]}"; do [[ "$r" == "$name" ]] && found=true && break; done
    [[ "$found" == false ]] && orphaned_skills+=("$d")
  done

  if [[ ${#orphaned_skills[@]} -gt 0 ]]; then
    echo "Orphaned skills (not in repo):"
    for d in "${orphaned_skills[@]}"; do echo "  $d"; done
  else
    echo "  No orphaned skills found."
  fi
fi

echo ""
echo "aurorie-teams $REPO_VERSION installed to $TARGET/"
