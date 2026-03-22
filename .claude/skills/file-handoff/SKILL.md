# File Handoff Protocol

Required skill for all agents. Use for every artifact write and context read.

## Writing Output
1. Create artifact directory via Bash tool:
   `mkdir -p .claude/workspace/artifacts/<team>/<task-id>/`
2. Write primary output files using lowercase kebab-case names
   (e.g., `prd.md`, `code-review.md`, `seo-report.md`).
3. Write `summary.md` last — one paragraph: what was produced, where it lives, key findings.
4. Update `status` in the task file to `"completed"` or `"failed"` using the Write tool.
5. Return the contents of `summary.md` as your Agent tool response (max 400 words).

## Reading Input
1. Read the task file at the path provided in your invocation prompt.
2. Read `description` for the task goal.
3. Scan `input_context` line by line. For any line starting with `artifact: `,
   read that file path before starting work.

## Artifact Naming
- Lowercase kebab-case only (e.g., `frontend-implementation.md`, `market-analysis.md`).
- No spaces or special characters.
- One primary output file per specialist agent execution.
