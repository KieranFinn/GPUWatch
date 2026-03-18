"""Configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path


# --- Paths ---
DB_PATH: str = os.getenv("GPUWATCH_DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "gpuwatch.db"))

# --- Telegram ---
TG_BOT_TOKEN: str = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID: str = os.getenv("TG_CHAT_ID", "")

# --- API ---
API_PORT: int = int(os.getenv("GPUWATCH_API_PORT", "8765"))
API_HOST: str = os.getenv("GPUWATCH_API_HOST", "0.0.0.0")

# --- Providers ---
# Comma-separated list; empty means "all available".
_raw_providers = os.getenv("GPUWATCH_PROVIDERS", "")
PROVIDERS: list[str] = [p.strip() for p in _raw_providers.split(",") if p.strip()] if _raw_providers else []

# --- Collection ---
COLLECT_TIMEOUT: int = int(os.getenv("GPUWATCH_COLLECT_TIMEOUT", "120"))
