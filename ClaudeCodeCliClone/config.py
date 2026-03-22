"""
Configuration management.
Settings are saved to ~/.claude_clone_config.json so they persist across sessions.
"""

import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude_clone_config.json"

DEFAULTS = {
    # Ollama server
    "ollama_host": "http://localhost:11434",

    # ---------------------------------------------------------------
    # Recommended models for your hardware (Xeon 2690v4, 64 GB RAM):
    #
    #   Architect (plans, reasons):
    #     - qwen2.5-coder:14b   → best quality/speed balance on CPU
    #     - deepseek-r1:14b     → explicit <think> reasoning, slower but smarter
    #     - qwen2.5-coder:32b   → maximum quality (~2-3 tok/s on CPU)
    #
    #   Worker (executes, writes code):
    #     - qwen2.5-coder:7b    → fast, great code quality, native tool-calling
    #     - qwen2.5-coder:14b   → better quality, ~4-6 tok/s on CPU
    #
    # Install:
    #   ollama pull qwen2.5-coder:14b
    #   ollama pull qwen2.5-coder:7b
    # ---------------------------------------------------------------
    "architect_model": "qwen2.5-coder:14b",
    "worker_model":    "qwen2.5-coder:7b",

    # Context window (tokens). 16k is safe for most tasks.
    # Reduce to 8192 if you run out of RAM.
    "context_window": 16384,

    # Max tool-calling iterations per agent per request
    "max_iterations": 20,
}


class Config:
    def __init__(self):
        self._data = DEFAULTS.copy()
        self._load()

    def _load(self):
        if CONFIG_PATH.exists():
            try:
                with CONFIG_PATH.open(encoding='utf-8') as f:
                    saved = json.load(f)
                self._data.update(saved)
            except Exception:
                pass  # Corrupt config → use defaults

    def save(self):
        CONFIG_PATH.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding='utf-8',
        )

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self.save()

    # Convenience properties
    @property
    def ollama_host(self) -> str:
        return self._data["ollama_host"]

    @property
    def architect_model(self) -> str:
        return self._data["architect_model"]

    @property
    def worker_model(self) -> str:
        return self._data["worker_model"]

    @property
    def context_window(self) -> int:
        return int(self._data["context_window"])

    @property
    def max_iterations(self) -> int:
        return int(self._data["max_iterations"])
