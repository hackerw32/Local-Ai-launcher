#!/usr/bin/env python3
"""
Claude Code CLI Clone
─────────────────────────────────────────────────────────────────────
A local AI coding assistant that mimics Claude Code:
  • Architect AI  — explores the codebase, creates a precise plan
  • Worker AI     — reads files, implements the plan, verifies output

Both agents use tool calling (read_file, write_file, run_command, …)
through a local Ollama server. No cloud, no API keys, no cost.

Usage:
  python main.py                # work in the current directory
  python main.py /path/to/proj  # work in a specific directory
─────────────────────────────────────────────────────────────────────
"""

import os
import sys
import atexit
from pathlib import Path

# ── Check Python version ───────────────────────────────────────────
if sys.version_info < (3, 9):
    print("Python 3.9 or newer is required.")
    sys.exit(1)

# ── Optional readline (better CLI experience) ──────────────────────
try:
    import readline
    _HISTORY = Path.home() / ".claude_clone_history"
    try:
        readline.read_history_file(str(_HISTORY))
    except FileNotFoundError:
        pass
    readline.set_history_length(2000)
    atexit.register(readline.write_history_file, str(_HISTORY))
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

# ── Check ollama package ───────────────────────────────────────────
try:
    import ollama as ollama_lib
except ImportError:
    print("Missing dependency: ollama")
    print("Install with:  pip install ollama rich")
    sys.exit(1)

from config import Config
from ui import UI
from agent import ArchitectAgent, WorkerAgent


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def get_project_path() -> Path:
    if len(sys.argv) > 1:
        p = Path(sys.argv[1]).resolve()
        if not p.exists():
            print(f"Error: path does not exist: {p}")
            sys.exit(1)
        return p
    return Path.cwd()


def check_model_available(model_name: str, available: list, ui: UI, role: str):
    """Warn if the configured model is not pulled yet."""
    # Match on base name (e.g. "qwen2.5-coder" matches "qwen2.5-coder:14b")
    base = model_name.split(":")[0]
    if not any(m.startswith(base) for m in available):
        ui.warning(
            f"{role} model '{model_name}' not found in Ollama. "
            f"Pull it with:  ollama pull {model_name}"
        )


def handle_slash_command(
    cmd: str,
    config: Config,
    ui: UI,
    architect_ref: list,
    worker_ref: list,
    client: ollama_lib.Client,
    project_path: Path,
) -> bool:
    """
    Handle /commands. Returns True if the input was a valid command.
    architect_ref / worker_ref are single-element lists used as mutable references
    so we can replace the agent objects when the model changes.
    """
    parts = cmd.strip().split(maxsplit=2)
    command = parts[0].lower()

    if command in ("/help", "/?"):
        ui.print_help()
        return True

    if command == "/models":
        ui.print_model_config(config)
        return True

    if command == "/clear":
        ui.clear()
        return True

    if command in ("/quit", "/exit", "/q"):
        ui.info("Goodbye!")
        sys.exit(0)

    if command == "/set" and len(parts) >= 3:
        key, value = parts[1].lower(), parts[2]
        if key == "architect":
            config.set("architect_model", value)
            architect_ref[0] = ArchitectAgent(value, client, project_path, ui)
            ui.success(f"Architect model → {value}")
        elif key == "worker":
            config.set("worker_model", value)
            worker_ref[0] = WorkerAgent(value, client, project_path, ui)
            ui.success(f"Worker model → {value}")
        elif key == "host":
            config.set("ollama_host", value)
            ui.success(f"Ollama host → {value}")
            ui.info("Restart the tool for the host change to take effect.")
        else:
            ui.error(f"Unknown setting: '{key}'.  Use: architect | worker | host")
        return True

    return False


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main():
    ui = UI()
    config = Config()

    ui.print_banner()

    # ── Connect to Ollama ─────────────────────────────────────────
    client = ollama_lib.Client(host=config.ollama_host)
    try:
        models_resp = client.list()
        available = [m.model for m in models_resp.models]
    except Exception as e:
        ui.error(f"Cannot connect to Ollama at {config.ollama_host}")
        ui.error(str(e))
        ui.info("Start Ollama with:  ollama serve")
        sys.exit(1)

    if not available:
        ui.warning("No models found in Ollama.")
        ui.info("Pull a model:  ollama pull qwen2.5-coder:7b")
        sys.exit(1)

    ui.print_models(available)

    # ── Warn about missing models ─────────────────────────────────
    check_model_available(config.architect_model, available, ui, "Architect")
    check_model_available(config.worker_model,    available, ui, "Worker")

    # ── Project path ──────────────────────────────────────────────
    project_path = get_project_path()
    ui.info(f"Project : {project_path}")
    ui.info(f"Architect model : {config.architect_model}")
    ui.info(f"Worker model    : {config.worker_model}")
    ui.info("Type /help for commands.\n")

    # ── Initialize agents (wrapped in a list for mutability) ──────
    architect_ref = [ArchitectAgent(config.architect_model, client, project_path, ui)]
    worker_ref    = [WorkerAgent   (config.worker_model,    client, project_path, ui)]

    # ── Conversation context (shared across turns) ────────────────
    # We keep a rolling window so the agents remember what happened earlier.
    conversation_context: list = []

    # ──────────────────────────────────────────────────────────────
    # Main REPL loop
    # ──────────────────────────────────────────────────────────────
    while True:
        try:
            if HAS_READLINE:
                user_input = input(ui.prompt()).strip()
            else:
                # rich prompt workaround — print the prompt separately
                print(ui.prompt(), end="", flush=True)
                user_input = input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            ui.info("Goodbye!")
            break

        if not user_input:
            continue

        # ── Slash commands ────────────────────────────────────────
        if user_input.startswith("/"):
            handle_slash_command(
                user_input, config, ui,
                architect_ref, worker_ref,
                client, project_path,
            )
            continue

        # ── Main flow: Architect → Worker ─────────────────────────
        try:
            # Phase 1 — Architect
            ui.thinking("Architect is exploring the codebase…")
            plan = architect_ref[0].create_plan(user_input, conversation_context)

            if not plan or not plan.strip():
                ui.warning("Architect returned an empty plan. Try rephrasing your request.")
                continue

            ui.plan(plan)

            # Phase 2 — Worker
            ui.thinking("Worker is implementing the plan…")
            result = worker_ref[0].execute_plan(plan, user_input)

            if result:
                ui.result(result)

            # ── Update rolling context ────────────────────────────
            conversation_context.append({"role": "user", "content": user_input})
            conversation_context.append({
                "role": "assistant",
                "content": f"**Plan:**\n{plan}\n\n**Result:**\n{result}",
            })
            # Keep only the last 5 exchanges (10 messages)
            if len(conversation_context) > 10:
                conversation_context = conversation_context[-10:]

        except KeyboardInterrupt:
            ui.warning("Interrupted.")
        except Exception as e:
            ui.error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
