#!/usr/bin/env python3
"""
v0.7 Demo Script — for use with QuickTime screen recording.

Usage:
  1. Open Terminal, maximize window, set font to 14-16pt
  2. Disable notification center (swipe with two fingers from top-right corner)
  3. Start QuickTime: File → New Screen Recording → record full screen
  4. Run: python3 demo/v0.7/demo_script.py
  5. Follow the timed narration below as a script

Output timing (total ~2:30):
  Part 1: 0:00 - 0:40
  Part 2: 0:40 - 1:10
  Part 3: 1:10 - 2:00
  Close:  2:00 - 2:30
"""

import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
HISTORY_FILE = PROJECT_ROOT / ".claude/workspace/execution_history.jsonl"

# ─── Styling ─────────────────────────────────────────────────────────────────

C = {
    "header": "\033[1;34m",
    "part": "\033[1;33m",
    "narrator": "\033[36m",
    "cmd": "\033[32m",
    "key": "\033[35m",
    "reset": "\033[0m",
}

def p(text, style=None, delay=0.4):
    if style:
        print(f"{C.get(style, '')}{text}{C['reset']}")
    else:
        print(text)
    sys.stdout.flush()
    time.sleep(delay)


def narrator(text):
    p(f"  # {text}", "narrator", delay=1.2)


def cmd(text):
    for line in text.split("\n"):
        p(f"  {line}", "cmd", delay=0.15)
    time.sleep(0.3)


def key(text):
    p(f"\n  ★ {text}\n", "key", delay=1.5)


def section(part_num, title):
    p(f"\n{'='*58}", "header")
    p(f" PART {part_num}: {title.upper()}", "part")
    p(f"{'='*58}\n", "header", delay=0.6)


# ─── Part 1 ───────────────────────────────────────────────────────────────────

def part1():
    section("1", "Fresh Run — No History")

    narrator("Let's run the orchestrator with no feedback history.")
    narrator("First, clear any existing history to start fresh.")

    cmd(f"rm -f {HISTORY_FILE}")
    cmd("ls .claude/workspace/")
    narrator("History file removed. Now run the orchestrator:")

    cmd('@orchestrator --feedback "Build a SaaS landing page"')
    cmd("")
    cmd("backend:")
    cmd("  raw_score: 3")
    cmd("  runs: 0")
    cmd("  success_rate: N/A")
    cmd("  feedback_bias: 1.0")
    cmd("  adjusted_score: 3.0")
    cmd("  confidence: high")
    cmd("")
    cmd("frontend:")
    cmd("  raw_score: 3")
    cmd("  runs: 0")
    cmd("  success_rate: N/A")
    cmd("  feedback_bias: 1.0")
    cmd("  adjusted_score: 3.0")
    cmd("  confidence: high")

    key("All teams at bias 1.0 — no history yet.")


# ─── Part 2 ───────────────────────────────────────────────────────────────────

def part2():
    section("2", "History Accumulated")

    narrator("17 runs have been logged since then.")
    narrator("Let's check what the system has learned:")

    cmd("@orchestrator --feedback-history")
    cmd("")
    cmd("Total events: 17")
    cmd("")
    cmd("Teams:")
    cmd("  backend:")
    cmd("    runs: 5")
    cmd("    success_rate: 0.4   ← 40%")
    cmd("    success_rate_display: \"0.4\" (5 runs)")
    cmd("")
    cmd("Templates:")
    cmd("  data-first:  runs=6, success_rate=0.83, bias=1.0")
    cmd("  linear:       runs=6, success_rate=0.67, bias=0.9")
    cmd("  flat:         runs=5, success_rate=0.40, bias=0.75")

    narrator("backend has a 40% success rate → bias drops to 0.75")
    narrator("The data-first template is the historical top performer.")


# ─── Part 3 ───────────────────────────────────────────────────────────────────

def part3():
    section("3", "Same Prompt — Different Decision")

    narrator("Now run the exact same prompt again:")
    narrator("Same routing rules. Same prompt. But history exists.")

    cmd('@orchestrator --feedback "Build a SaaS landing page"')
    cmd("")
    cmd("backend:")
    cmd("  raw_score: 3")
    cmd("  runs: 5")
    cmd("  success_rate: 0.4")
    cmd("  feedback_bias: 0.75     ← from history")
    cmd("  adjusted_score: 2.25    ← 3 × 0.75")
    cmd("  confidence: medium       ← dropped from high!")
    cmd("")
    cmd("frontend:")
    cmd("  raw_score: 3")
    cmd("  runs: 6")
    cmd("  success_rate: 0.67")
    cmd("  feedback_bias: 0.9")
    cmd("  adjusted_score: 2.7")
    cmd("  confidence: medium")

    narrator("Watch backend: raw_score is still 3.")
    narrator("Nothing changed in the routing rules.")

    key("Only the history changed — and the decision changed.")

    narrator("If dispatch policy requires confirmation for medium confidence,")
    narrator("this task now pauses and asks.")
    narrator("Without history, it would have auto-dispatched.")

    cmd("")
    cmd("Template candidates:")
    cmd("  data-first:  runs=6, success_rate=0.83, bias=1.0  ✓ selected")
    cmd("  linear:       runs=6, success_rate=0.67, bias=0.9")
    cmd("  flat:         runs=5, success_rate=0.40, bias=0.75")


# ─── Closing ──────────────────────────────────────────────────────────────────

def closing():
    section("CLOSE", "The Feedback Loop")

    cmd("Task completes → event written (append-only JSONL)")
    cmd("                        ↓")
    cmd("  Next routing → reads history → adjusts score")
    cmd("                        ↓")
    cmd("  Adjusted score → confidence band → dispatch policy")
    cmd("")

    narrator("Not ML. Not autonomous.")
    narrator("Rule-based. Explainable. Conservative.")

    key("The system doesn't just execute anymore.")

    key("It improves how it executes.")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    p("\n\033[1;34m╔══════════════════════════════════════════════════════════╗\033[0m")
    p("\033[1;34m║          v0.7 Demo — starting in 3 seconds...              ║\033[0m")
    p("\033[1;34m║  (QuickTime should already be recording)                  ║\033[0m")
    p("\033[1;34m╚══════════════════════════════════════════════════════════╝\033[0m\n")
    time.sleep(3)

    # Seed history
    section("SETUP", "Seeding History")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "demo/v0.7/seed_history.py")],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.strip().split("\n"):
        if line.strip():
            p(f"  {line}", "cmd", delay=0.1)
    time.sleep(0.5)

    p(f"\n  \033[1;32m→ Recording started. Good luck!\033[0m\n")
    time.sleep(2)

    part1()
    time.sleep(1)
    part2()
    time.sleep(1)
    part3()
    closing()

    p("\n\033[1;32m✓ Demo complete. Stop QuickTime recording.\033[0m\n")
    p("  Save as: demo_v0.7.mp4")


if __name__ == "__main__":
    main()
