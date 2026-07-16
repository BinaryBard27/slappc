"""Improved slap detection logic."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class DetectionResult:
    """Result of one detector pass."""

    detected: bool
    force_ratio: float = 0.0
    peak: float = 0.0
    noise_floor: float = 0.0


class SlapDetector:
    """Peak-aware detector with ambient calibration."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.noise_floor = 0.01
        self.last_slap_time = 0.0
        self.calibrating = False
        self._calibration_levels: list[float] = []
        self._calibration_target = 40

    @staticmethod
    def _rms(samples: np.ndarray) -> float:
        samples = samples.astype(np.float64)
        return float(np.sqrt(np.mean(samples**2)))

    @staticmethod
    def _peak(samples: np.ndarray) -> float:
        return float(np.max(np.abs(samples.astype(np.float64))))

    def calibrate_start(self, target_samples: int = 40) -> None:
        """Begin ambient calibration."""
        self.calibrating = True
        self._calibration_levels = []
        self._calibration_target = max(10, target_samples)

    def calibrate_step(self, samples: np.ndarray) -> Optional[float]:
        """Feed calibration audio, returning the final floor when ready."""
        level = self._rms(samples)
        self._calibration_levels.append(level)
        if len(self._calibration_levels) >= self._calibration_target:
            self.noise_floor = float(np.median(self._calibration_levels) * 1.6)
            self.calibrating = False
            return self.noise_floor
        return None

    def process(self, samples: np.ndarray, sensitivity: float, cooldown: float) -> DetectionResult:
        """Analyze one chunk of audio and return a detection result."""
        rms = self._rms(samples)
        peak = self._peak(samples)

        if self.calibrating:
            floor = self.calibrate_step(samples)
            return DetectionResult(False, 0.0, peak, self.noise_floor if floor is None else floor)

        self.noise_floor = self.noise_floor * 0.995 + rms * 0.005
        sensitivity = max(0.0, min(1.0, float(sensitivity)))
        cooldown = max(0.05, float(cooldown))

        trigger_level = self.noise_floor * (1.8 + sensitivity * 5.0)
        peak_gate = max(self.noise_floor * 2.5, 1800.0 - sensitivity * 700.0)
        peak_dropout = peak < 32000.0
        mild_rms_gate = rms > self.noise_floor * (1.2 + sensitivity)
        in_cooldown = time.time() - self.last_slap_time < cooldown

        if not in_cooldown and rms > trigger_level and peak > peak_gate and peak_dropout and mild_rms_gate:
            self.last_slap_time = time.time()
            force_ratio = min(1.0, max(0.0, (rms - trigger_level) / max(trigger_level, 1e-6)))
            return DetectionResult(True, force_ratio, peak, self.noise_floor)

        return DetectionResult(False, 0.0, peak, self.noise_floor)
