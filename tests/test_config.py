import tempfile
import logging
import unittest
from pathlib import Path

from config import ConfigStore
from logger import configure_logging


class ConfigTests(unittest.TestCase):
    def test_defaults_validate_and_save_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            logger = configure_logging(tmp)
            try:
                path = Path(tmp) / "config.json"
                store = ConfigStore(str(path), logger)
                store.data["sensitivity"] = 2.0
                store.data["cooldown"] = -1
                store.data["volume"] = 9
                store.validate()
                self.assertEqual(store.data["sensitivity"], 1.0)
                self.assertEqual(store.data["cooldown"], 0.05)
                self.assertEqual(store.data["volume"], 1.0)
                store.save()
                fresh = ConfigStore(str(path), logger)
                fresh.load()
                self.assertEqual(fresh.data["sensitivity"], 1.0)
            finally:
                logging.shutdown()


if __name__ == "__main__":
    unittest.main()
