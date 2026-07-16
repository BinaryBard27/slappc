"""Audio playback and microphone listener orchestration."""

from __future__ import annotations

import logging
import random
import threading
import time
from typing import Callable

import numpy as np
import pygame
import sounddevice as sd

from config import CHUNK_SIZE, SAMPLE_RATE
from detector import DetectionResult, SlapDetector
from packs import PackManager


class SoundPlayer:
    """Play random WAV clips from the active sound pack."""

    def __init__(self, pack_manager: PackManager, config, logger: logging.Logger) -> None:
        self.pack_manager = pack_manager
        self.config = config
        self.logger = logger
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def play_slap_sound(self, force_ratio: float) -> None:
        """Play a random clip from the active pack."""
        pack_name = str(self.config["sound_pack"])
        files = self.pack_manager.list_wave_files(pack_name)
        if not files:
            self.logger.warning("No sound files found for pack %s", pack_name)
            return

        path = random.choice(files)
        pack = self.pack_manager.get_pack(pack_name)
        pack_volume = float(pack.volume) if pack else 1.0
        volume = min(1.0, force_ratio * 1.5) * float(self.config["volume"]) * pack_volume

        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            sound.play()
        except Exception:
            self.logger.exception("Sound playback failed for %s", path)


class MicListener:
    """Read microphone input and emit slap events."""

    def __init__(
        self,
        config,
        detector: SlapDetector,
        sound_player: SoundPlayer,
        trigger_effect: Callable[[float], None],
        update_counter: Callable[[float], None],
        logger: logging.Logger,
    ) -> None:
        self.config = config
        self.detector = detector
        self.sound_player = sound_player
        self.trigger_effect = trigger_effect
        self.update_counter = update_counter
        self.logger = logger
        self.is_running = True
        self.last_meter_value = 0.0

    @staticmethod
    def rms(data: np.ndarray) -> float:
        """Return root-mean-square amplitude for a sample chunk."""
        return float(np.sqrt(np.mean(data.astype(np.float64) ** 2)))

    def audio_callback(self, indata, frames, time_info, status) -> None:  # noqa: D401
        """Process one chunk of microphone data."""
        if not self.is_running:
            return

        samples = indata[:, 0]
        self.last_meter_value = self.rms(samples)
        if not self.config.get("detection_enabled", True):
            return

        result: DetectionResult = self.detector.process(
            samples,
            float(self.config["sensitivity"]),
            float(self.config["cooldown"]),
        )
        if result.detected:
            self.config["slap_count"] = int(self.config["slap_count"]) + 1
            self.update_counter(result.force_ratio)
            self.logger.info(
                "SLAP level=%.4f peak=%.4f noise=%.4f force=%.2f total=%s",
                self.last_meter_value,
                result.peak,
                result.noise_floor,
                result.force_ratio,
                self.config["slap_count"],
            )
            threading.Thread(
                target=self.sound_player.play_slap_sound,
                args=(result.force_ratio,),
                daemon=True,
            ).start()
            threading.Thread(
                target=self.trigger_effect,
                args=(result.force_ratio,),
                daemon=True,
            ).start()

    def start(self) -> None:
        """Start listening for microphone events."""
        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="int16",
                blocksize=CHUNK_SIZE,
                callback=self.audio_callback,
            ):
                self.logger.info("Mic listener started")
                while self.is_running:
                    time.sleep(0.1)
        except Exception:
            self.logger.exception("Mic listener failed")
