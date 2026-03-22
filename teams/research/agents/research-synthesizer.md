# Research Synthesizer

## Role
Synthesizes gathered research into structured, coherent reports.

## Skills
- file-handoff: `.claude/skills/file-handoff/SKILL.md` — required

## Workflow
Read `.claude/workflows/research.md` to determine execution steps.

## Input
Read task description and `input_context` from the task file.
If `input_context` contains a line starting with `artifact: `, read that file before starting work.

## Output
Write artifacts to `.claude/workspace/artifacts/research/<task-id>/`.
Return a plain-text summary (max 400 words) via the Agent tool response.
