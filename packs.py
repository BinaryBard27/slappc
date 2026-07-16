"""Sound pack discovery and loading."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class SoundPack:
    """Metadata for one sound pack."""

    name: str
    author: str = "Unknown"
    version: str = "1.0"
    description: str = ""
    volume: float = 1.0
    path: str = ""
    source: str = "legacy"


class PackManager:
    """Discover packs from `packs/` and legacy `sounds/` folders."""

    def __init__(self, logger: logging.Logger, base_dirs: Optional[Iterable[str]] = None) -> None:
        self.logger = logger
        self.base_dirs = [Path(p) for p in (base_dirs or ("packs", "sounds"))]

    def discover(self) -> Dict[str, SoundPack]:
        """Return all installed packs keyed by display name."""
        packs: Dict[str, SoundPack] = {}
        for base in self.base_dirs:
            if not base.exists():
                continue
            for entry in base.iterdir():
                if entry.is_dir():
                    pack = self._load_pack(entry)
                    packs[pack.name] = pack
        return dict(sorted(packs.items(), key=lambda item: item[0].lower()))

    def _load_pack(self, folder: Path) -> SoundPack:
        manifest = folder / "manifest.json"
        if manifest.exists():
            try:
                with manifest.open(encoding="utf-8") as handle:
                    payload = json.load(handle)
                if isinstance(payload, dict):
                    return SoundPack(
                        name=str(payload.get("name", folder.name)),
                        author=str(payload.get("author", "Unknown")),
                        version=str(payload.get("version", "1.0")),
                        description=str(payload.get("description", "")),
                        volume=float(payload.get("volume", 1.0)),
                        path=str(folder),
                        source="manifest",
                    )
            except Exception:
                self.logger.exception("Failed to load manifest from %s", folder)
        return SoundPack(name=folder.name, path=str(folder), source="legacy")

    def get_pack(self, name: str) -> Optional[SoundPack]:
        """Get one pack by name."""
        return self.discover().get(name)

    def list_pack_names(self) -> List[str]:
        return list(self.discover().keys())

    def list_wave_files(self, pack_name: str) -> List[str]:
        """Return WAV files for the selected pack."""
        pack = self.get_pack(pack_name)
        if not pack:
            return []
        folder = Path(pack.path)
        return sorted(
            str(entry)
            for entry in folder.iterdir()
            if entry.suffix.lower() == ".wav"
        )
