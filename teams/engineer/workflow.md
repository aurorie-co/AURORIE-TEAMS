# Engineer Workflow

## Feature Development
Trigger: new feature request or code change task

Steps:
1. engineer-lead reviews requirements and creates task breakdown
2. Assign to engineer-backend and/or engineer-frontend based on scope
3. engineer-qa validates acceptance criteria
4. Write output to `.claude/workspace/artifacts/engineer/<task-id>/`

## Bug Fix
Trigger: bug report or failing test

Steps:
1. engineer-lead identifies affected component
2. Assign to relevant specialist
3. engineer-qa verifies fix
4. Write output to `.claude/workspace/artifacts/engineer/<task-id>/`
