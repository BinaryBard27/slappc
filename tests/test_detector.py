import tempfile
import logging
import unittest

import numpy as np

from detector import SlapDetector
from logger import configure_logging


class DetectorTests(unittest.TestCase):
    def test_calibration_and_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            logger = configure_logging(tmp)
            try:
                detector = SlapDetector(logger)
                detector.calibrate_start(10)
                for _ in range(10):
                    detector.calibrate_step(np.zeros(1024, dtype=np.int16))
                self.assertFalse(detector.calibrating)
                loud = np.concatenate(
                    [
                        np.zeros(1000, dtype=np.int16),
                        np.array([30000, -30000, 30000, -30000], dtype=np.int16),
                    ]
                )
                result = detector.process(loud, 0.3, 0.1)
                self.assertTrue(result.detected)
                self.assertGreater(result.force_ratio, 0.0)
            finally:
                logging.shutdown()


if __name__ == "__main__":
    unittest.main()
