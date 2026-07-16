import logging
import tempfile
import unittest
from pathlib import Path

from logger import configure_logging
from stats import StatisticsStore


class StatsTests(unittest.TestCase):
    def test_record_slap_updates_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            logger = configure_logging(tmp)
            try:
                store = StatisticsStore(str(Path(tmp) / "stats.json"), logger)
                store.load()
                unlocked = store.record_slap(1.0)
                summary = store.summary()
                self.assertEqual(summary["today"], 1)
                self.assertEqual(summary["lifetime"], 1)
                self.assertGreaterEqual(summary["strongest"], 1.0)
                self.assertIn("First Slap", unlocked)
            finally:
                logging.shutdown()


if __name__ == "__main__":
    unittest.main()
