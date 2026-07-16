"""Persistent slap statistics and achievements."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List


ACHIEVEMENTS = {
    "First Slap": lambda store: store.lifetime_slaps >= 1,
    "10 Slaps": lambda store: store.lifetime_slaps >= 10,
    "100 Slaps": lambda store: store.lifetime_slaps >= 100,
    "1000 Slaps": lambda store: store.lifetime_slaps >= 1000,
    "Maximum Force": lambda store: store.strongest_slap >= 0.95,
    "One Hour Session": lambda store: store.longest_session_minutes >= 60,
}


@dataclass
class SessionStats:
    """Mutable session data."""

    slap_count: int = 0
    session_start: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    strongest_slap: float = 0.0
    force_total: float = 0.0


class StatisticsStore:
    """Track, persist, and summarize usage stats."""

    def __init__(self, stats_path: str, logger: logging.Logger) -> None:
        self.path = Path(stats_path)
        self.logger = logger
        self.data: Dict[str, object] = {
            "lifetime_slaps": 0,
            "daily_history": {},
            "sessions": [],
            "achievements": [],
            "strongest_slap": 0.0,
            "average_force": 0.0,
        }
        self.session = SessionStats()

    def load(self) -> Dict[str, object]:
        if self.path.exists():
            try:
                with self.path.open(encoding="utf-8") as handle:
                    saved = json.load(handle)
                if isinstance(saved, dict):
                    self.data.update(saved)
            except Exception:
                self.logger.exception("Failed to load stats; starting fresh")
        return self.data

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2)

    def record_slap(self, force_ratio: float) -> List[str]:
        """Update lifetime and daily metrics for a new slap."""
        today = date.today().isoformat()
        self.session.slap_count += 1
        self.session.force_total += force_ratio
        self.session.strongest_slap = max(self.session.strongest_slap, force_ratio)

        self.data["lifetime_slaps"] = int(self.data.get("lifetime_slaps", 0)) + 1
        daily = dict(self.data.get("daily_history", {}))
        daily[today] = int(daily.get(today, 0)) + 1
        self.data["daily_history"] = daily
        self.data["strongest_slap"] = max(float(self.data.get("strongest_slap", 0.0)), force_ratio)
        self.data["average_force"] = self.session.force_total / max(self.session.slap_count, 1)

        unlocked = self._unlock_achievements()
        self.save()
        return unlocked

    def end_session(self) -> None:
        """Persist the current session summary."""
        session_minutes = (
            datetime.now(timezone.utc) - datetime.fromisoformat(self.session.session_start)
        ).total_seconds() / 60.0
        sessions = list(self.data.get("sessions", []))
        sessions.append(
            {
                "started_at": self.session.session_start,
                "ended_at": datetime.now(timezone.utc).isoformat(),
                "slaps": self.session.slap_count,
                "strongest_slap": self.session.strongest_slap,
                "average_force": self.data.get("average_force", 0.0),
                "minutes": round(session_minutes, 2),
            }
        )
        self.data["sessions"] = sessions
        self.save()

    @property
    def lifetime_slaps(self) -> int:
        return int(self.data.get("lifetime_slaps", 0))

    @property
    def strongest_slap(self) -> float:
        return float(self.data.get("strongest_slap", 0.0))

    @property
    def longest_session_minutes(self) -> float:
        sessions = self.data.get("sessions", [])
        if not isinstance(sessions, list) or not sessions:
            return 0.0
        values = [
            float(session.get("minutes", 0.0))
            for session in sessions
            if isinstance(session, dict)
        ]
        return max(values) if values else 0.0

    def summary(self) -> Dict[str, object]:
        today = date.today().isoformat()
        return {
            "today": int(dict(self.data.get("daily_history", {})).get(today, 0)),
            "lifetime": self.lifetime_slaps,
            "strongest": self.strongest_slap,
            "average_force": float(self.data.get("average_force", 0.0)),
            "sessions": len(self.data.get("sessions", [])),
            "daily_history": self.data.get("daily_history", {}),
            "achievements": self.data.get("achievements", []),
        }

    def _unlock_achievements(self) -> List[str]:
        unlocked: List[str] = []
        existing = set(self.data.get("achievements", []))
        for name, predicate in ACHIEVEMENTS.items():
            if name not in existing and predicate(self):
                existing.add(name)
                unlocked.append(name)
        self.data["achievements"] = sorted(existing)
        return unlocked
