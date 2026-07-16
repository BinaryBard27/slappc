"""Application configuration management."""

from __future__ import annotations

import json
import logging
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Tuple


DEFAULT_CONFIG: Dict[str, Any] = {
    "sensitivity": 0.35,
    "cooldown": 1.0,
    "sound_pack": "Default",
    "volume": 1.0,
    "detection_enabled": True,
    "minimize_to_tray": True,
    "usb_moaner": False,
    "launch_at_login": False,
    "slap_count": 0,
    "screen_flash": True,
    "screen_shake": True,
    "comic_text": True,
    "glass_crack": False,
    "confetti": False,
    "disable_effects": False,
}

SAMPLE_RATE = 44100
CHUNK_SIZE = 1024
IMPACT_WINDOW = 0.05
BASELINE_FRAMES = 20

ConfigNotes = Tuple[str, ...]


def _parse_bool(value: Any, default: bool) -> bool:
    """Parse common config boolean representations safely."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return default


class ConfigStore:
    """Load and persist the app's JSON config."""

    def __init__(self, config_path: str, logger: logging.Logger) -> None:
        self.path = Path(config_path)
        self.logger = logger
        self.data: Dict[str, Any] = deepcopy(DEFAULT_CONFIG)

    def load(self) -> Dict[str, Any]:
        """Load config from disk, merging it with defaults."""
        if self.path.exists():
            try:
                with self.path.open(encoding="utf-8") as handle:
                    saved = json.load(handle)
                if isinstance(saved, dict):
                    self.data.update(saved)
            except Exception:
                self.logger.exception("Failed to load config; using defaults")
        return self.data

    def validate(self) -> ConfigNotes:
        """Coerce values into safe ranges."""
        self.data["sensitivity"] = max(0.0, min(1.0, float(self.data.get("sensitivity", 0.35))))
        self.data["cooldown"] = max(0.05, min(10.0, float(self.data.get("cooldown", 1.0))))
        self.data["volume"] = max(0.0, min(1.0, float(self.data.get("volume", 1.0))))
        for key in (
            "detection_enabled",
            "minimize_to_tray",
            "usb_moaner",
            "launch_at_login",
            "screen_flash",
            "screen_shake",
            "comic_text",
            "glass_crack",
            "confetti",
            "disable_effects",
        ):
            self.data[key] = _parse_bool(self.data.get(key, DEFAULT_CONFIG[key]), DEFAULT_CONFIG[key])
        if not isinstance(self.data.get("sound_pack"), str):
            self.data["sound_pack"] = DEFAULT_CONFIG["sound_pack"]
        return ("validated",)

    def save(self) -> None:
        """Persist the current config to disk."""
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def reset_defaults(self) -> Dict[str, Any]:
        """Restore default values."""
        self.data = deepcopy(DEFAULT_CONFIG)
        return self.data
