"""
Verification command execution for v0.9 — pure validation + side-effectful runner.

Pure functions:
  - validate_verification_command(cmd)  → raises ValueError if invalid

Side-effectful:
  - run_verification(node)  → executes verification_command, returns exit_code int
"""

import subprocess
import shlex
from pathlib import Path
from typing import Optional

# v0.9 hardcoded allowlist — token-based (argv[0]), not substring
_ALLOWED_PREFIXES = ("python3", "pytest", "bash", "sh")

# Shell operators that indicate unsafe/multi-command usage
_FORBIDDEN_CHARS = ("|", "&&", "||", ";", ">", "<", "`", "$", "\n", "\r")


def validate_verification_command(command: str) -> None:
    """
    Validates a verification_command string against the v0.9 allowlist.

    Rules:
    - Command must start with an exact allowed token (token-based, not substring)
    - No shell operators (|, &&, ||, ;, >, <, `, $, newline)
    - No sudo, no rm -rf

    Raises:
        ValueError: if the command is invalid
    """
    if not command or not isinstance(command, str):
        raise ValueError("verification_command must be a non-empty string")

    # Token-based split: preserve the command name as first token
    tokens = shlex.split(command)
    if not tokens:
        raise ValueError("verification_command cannot be empty or whitespace-only")

    first_token = tokens[0]

    # Must start with an allowed prefix
    if first_token not in _ALLOWED_PREFIXES:
        raise ValueError(
            f"verification_command must start with one of {_ALLOWED_PREFIXES}, "
            f"got: {first_token!r}"
        )

    # No shell operators anywhere in the raw string
    for char in _FORBIDDEN_CHARS:
        if char in command:
            raise ValueError(
                f"verification_command contains forbidden character {char!r}: {command!r}"
            )

    # No dangerous commands
    lower_cmd = command.lower()
    if "sudo" in lower_cmd or "rm -rf" in lower_cmd:
        raise ValueError(f"verification_command contains dangerous command: {command!r}")


def run_verification(node: dict, cwd: Optional[str] = None) -> int:
    """
    Executes node["verification_command"] in a subprocess and returns the exit code.

    Args:
        node: a graph node dict with at least:
              - verification_command (str): the command to run
        cwd:  repository root path (resolved at dispatch time). Defaults to the
              repository root used by the orchestrator.

    Returns:
        int: subprocess exit code (0 = success, non-zero = failure)

    Raises:
        FileNotFoundError: if the executable is not found
        ValueError: if validation fails before execution

    Note:
        Execution failure (FileNotFoundError) and verification failure (exit != 0)
        are distinct:
        - FileNotFoundError → treat as node execution failure (orchestrator handles)
        - exit != 0         → verification failed → node status = failed
    """
    command = node.get("verification_command")
    if not command:
        raise ValueError("node has no verification_command")

    # Validate before running
    validate_verification_command(command)

    # Resolve working directory
    repo_root = cwd or str(Path(__file__).parent.parent)

    result = subprocess.run(
        shlex.split(command),   # split into argv tokens for subprocess
        shell=False,
        cwd=repo_root,
        capture_output=True,
    )
    return result.returncode
