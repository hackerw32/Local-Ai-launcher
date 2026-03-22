"""
Configuration management.
Settings are saved to ~/.claude_clone_config.json so they persist across sessions.
"""

import json
from pathlib import Path

CONFIG_PATH = Path.home() / ".claude_clone_config.json"

# ─────────────────────────────────────────────────────────────────
# Hardware profiles — switch with:  /profile cpu   or  /profile gpu
# ─────────────────────────────────────────────────────────────────
PROFILES = {
    "cpu": {
        # Xeon 2690v4, 64 GB RAM, no useful GPU (GT 1030 2 GB)
        # Total RAM used: ~13.5 GB   Speed: 4-12 tok/s
        "architect_model": "qwen2.5-coder:14b",   # 4-6 tok/s, ~9 GB RAM
        "worker_model":    "qwen2.5-coder:7b",    # 8-12 tok/s, ~4.5 GB RAM
        "context_window":  16384,
        "description": "CPU only (Xeon 2690v4 + 64 GB RAM)",
    },
    "gpu": {
        # RTX 5060 16 GB VRAM  (or similar 12-16 GB GPU)
        # Architect 32b: ~18 GB → partial offload, still much faster than CPU
        # Worker 14b: ~9 GB → fits fully in VRAM, ~50-70 tok/s
        "architect_model": "qwen2.5-coder:32b",   # 20-30 tok/s on GPU
        "worker_model":    "qwen2.5-coder:14b",   # 50-70 tok/s on GPU
        "context_window":  32768,
        "description": "GPU (RTX 5060 16 GB VRAM)",
    },
    # Alternative: deepseek-r1 for stronger reasoning (architect only)
    # /set architect deepseek-r1:14b   (cpu)
    # /set architect deepseek-r1:32b   (gpu)
}

DEFAULTS = {
    "ollama_host":     "http://localhost:11434",
    "architect_model": PROFILES["cpu"]["architect_model"],
    "worker_model":    PROFILES["cpu"]["worker_model"],
    "context_window":  PROFILES["cpu"]["context_window"],
    "active_profile":  "cpu",
    "max_iterations":  20,
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

    def apply_profile(self, profile_name: str) -> str:
        """Apply a hardware profile. Returns a status message."""
        if profile_name not in PROFILES:
            return f"Unknown profile '{profile_name}'. Available: {list(PROFILES.keys())}"
        p = PROFILES[profile_name]
        self._data["architect_model"] = p["architect_model"]
        self._data["worker_model"]    = p["worker_model"]
        self._data["context_window"]  = p["context_window"]
        self._data["active_profile"]  = profile_name
        self.save()
        return (
            f"Profile '{profile_name}' applied  ({p['description']})\n"
            f"  Architect → {p['architect_model']}\n"
            f"  Worker    → {p['worker_model']}\n"
            f"  Context   → {p['context_window']} tokens"
        )

    @property
    def active_profile(self) -> str:
        return self._data.get("active_profile", "cpu")

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
