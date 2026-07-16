import tempfile
import logging
import unittest
from pathlib import Path

from logger import configure_logging
from packs import PackManager


class PackManagerTests(unittest.TestCase):
    def test_discovers_manifest_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            logger = configure_logging(tmp)
            try:
                pack_dir = Path(tmp) / "packs" / "Default"
                pack_dir.mkdir(parents=True)
                (pack_dir / "manifest.json").write_text(
                    '{"name":"Default","author":"A","version":"1.0","description":"d","volume":0.8}',
                    encoding="utf-8",
                )
                (pack_dir / "slap1.wav").write_bytes(b"RIFF")
                manager = PackManager(logger, base_dirs=[str(Path(tmp) / "packs")])
                packs = manager.discover()
                self.assertIn("Default", packs)
                self.assertEqual(manager.list_wave_files("Default"), [str(pack_dir / "slap1.wav")])
            finally:
                logging.shutdown()


if __name__ == "__main__":
    unittest.main()
