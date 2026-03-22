# aurorie-teams

Company-wide Claude Code agent configuration library.

## Requirements

- macOS or Linux (bash 3.2+)
- `jq` — `brew install jq` / `apt install jq`
- `uuidgen` or `python3`
- Node.js (for `npx`-based MCP servers)

## Install

From your local project root:

    git clone https://github.com/aurorie/aurorie-teams.git /tmp/aurorie-teams
    cd /path/to/your-project
    /tmp/aurorie-teams/install.sh

## Flags

| Flag | Effect |
|------|--------|
| (none) | Default install |
| `--force-workflows` | Overwrite local workflow + routing.json overrides (prompts for confirmation) |
| `--yes` | Skip confirmation prompts (for CI, use with --force-workflows) |
| `--detect-orphans` | Report stale agent/skill files not in repo |

## Upgrade

    cd /tmp/aurorie-teams && git pull
    cd /path/to/your-project && /tmp/aurorie-teams/install.sh

## Environment Variables for MCP

Set these in your shell profile before starting Claude Code:

    export GITHUB_TOKEN=...
    export EXA_API_KEY=...
    export FIRECRAWL_API_KEY=...

## Customizing

- **Workflows:** Edit `.claude/workflows/<team>.md`
- **Routing:** Edit `.claude/routing.json`
- **CLAUDE.md:** Edit `CLAUDE.md` in your project root
