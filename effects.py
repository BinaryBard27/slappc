"""Visual feedback overlay for SlapPC 2.0."""

from __future__ import annotations

import logging
import random
import sys
import threading
import time
from typing import Optional, Tuple

import pygame


class VisualEffects:
    """Fullscreen overlay that renders slap feedback effects."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self.screen_width = 0
        self.screen_height = 0
        self.display_surface = None
        self.clock = None
        self.running = False
        self.effects_thread = None
        self.screen_shake_intensity = 0.0
        self.impact_flash_alpha = 0
        self.slap_marks = []
        self.comic_texts = []
        self.confetti_particles = []
        self.glass_cracks = []
        self.flash_color = (255, 100, 100)
        self.shake_color = (255, 50, 50)
        self.shake_decay = 0.95
        self.flash_decay = 0.85
        self.mark_lifetime = 2.0
        self._owns_pygame = False
        self._initialized = False
        self.options = {
            "screen_flash": True,
            "screen_shake": True,
            "comic_text": True,
            "glass_crack": False,
            "confetti": False,
            "disable_effects": False,
        }

    def _init_display(self) -> bool:
        try:
            if self.running and self.display_surface is not None:
                return True
            if not pygame.get_init():
                pygame.init()
                self._owns_pygame = True
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
            self.display_surface = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.NOFRAME | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA,
            )
            pygame.display.set_caption("SlapPC Effects")
            pygame.mouse.set_visible(False)
            if sys.platform == "win32":
                self._make_window_clickthrough()
            self.clock = pygame.time.Clock()
            self.running = True
            self.effects_thread = threading.Thread(target=self._render_loop, daemon=True)
            self.effects_thread.start()
            self._initialized = True
            self.logger.info("Visual effects initialized")
            return True
        except Exception:
            self.logger.exception("Failed to initialize visual effects")
            self._shutdown_display()
            self.running = False
            return False

    def _shutdown_display(self) -> None:
        """Best-effort cleanup for a partially initialized overlay."""
        self.running = False
        self.screen_shake_intensity = 0.0
        self.impact_flash_alpha = 0
        self.slap_marks.clear()
        self.comic_texts.clear()
        self.confetti_particles.clear()
        self.glass_cracks.clear()
        try:
            if self.display_surface:
                pygame.display.quit()
        except Exception:
            self.logger.exception("Failed to close visual effects display")
        finally:
            self.display_surface = None
            self.clock = None
            self.effects_thread = None
            if self._owns_pygame and pygame.get_init():
                try:
                    pygame.quit()
                except Exception:
                    self.logger.exception("Failed to shut down pygame after visual effects init failure")
                self._owns_pygame = False

    def _make_window_clickthrough(self) -> None:
        try:
            import win32con
            import win32gui

            hwnd = pygame.display.get_wm_info()["window"]
            win32gui.SetWindowLong(
                hwnd,
                win32con.GWL_EXSTYLE,
                win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                | win32con.WS_EX_LAYERED
                | win32con.WS_EX_TRANSPARENT,
            )
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                0,
                0,
                0,
                0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE,
            )
            win32gui.SetLayeredWindowAttributes(hwnd, win32gui.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)
        except ImportError:
            raise RuntimeError("pywin32 is required for click-through overlay on Windows")
        except Exception:
            raise

    def update_options(self, options) -> None:
        self.options.update(options)

    def trigger_slap_effect(self, force_ratio: float, position: Optional[Tuple[int, int]] = None) -> None:
        if self.options.get("disable_effects"):
            return
        if not self.running or not self.display_surface:
            if not self._init_display():
                self.options["disable_effects"] = True
                return
        if not self.running or not self.display_surface:
            return

        shake_intensity = min(15.0, force_ratio * 20.0)
        flash_alpha = int(100 + force_ratio * 155)
        if self.options.get("screen_shake", True):
            self.screen_shake_intensity = shake_intensity
        if self.options.get("screen_flash", True):
            self.impact_flash_alpha = flash_alpha

        if position is None:
            mark_x = random.randint(100, max(101, self.screen_width - 100))
            mark_y = random.randint(100, max(101, self.screen_height - 100))
        else:
            mark_x, mark_y = position

        mark_size = int(20 + force_ratio * 80)
        self.slap_marks.append(
            {
                "x": mark_x,
                "y": mark_y,
                "size": mark_size,
                "alpha": 255,
                "timestamp": time.time(),
                "force": force_ratio,
            }
        )
        if self.options.get("comic_text", True):
            self.comic_texts.append(
                {
                    "text": "SLAP!",
                    "x": mark_x,
                    "y": mark_y - 30,
                    "timestamp": time.time(),
                }
            )
        if self.options.get("confetti", False):
            for _ in range(20):
                self.confetti_particles.append(
                    {
                        "x": mark_x,
                        "y": mark_y,
                        "vx": random.uniform(-4.0, 4.0),
                        "vy": random.uniform(-7.0, -1.0),
                        "timestamp": time.time(),
                    }
                )
        if self.options.get("glass_crack", False):
            self.glass_cracks.append({"timestamp": time.time(), "strength": force_ratio})
        self.logger.info("Slap effect triggered force=%.2f shake=%.1f", force_ratio, shake_intensity)

    def _render_loop(self) -> None:
        while self.running:
            self.display_surface.fill((0, 0, 0, 0))
            shake_offset_x = 0
            shake_offset_y = 0

            if self.screen_shake_intensity > 0.1 and self.options.get("screen_shake", True):
                shake_offset_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
                shake_offset_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
                self.screen_shake_intensity *= self.shake_decay

            if self.screen_shake_intensity > 0.5 and self.options.get("screen_shake", True):
                shake_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                shake_alpha = int(self.screen_shake_intensity * 15)
                shake_surface.fill((*self.shake_color, shake_alpha))
                self.display_surface.blit(shake_surface, (shake_offset_x, shake_offset_y))

            if self.impact_flash_alpha > 0 and self.options.get("screen_flash", True):
                flash_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                flash_surface.fill((*self.flash_color, self.impact_flash_alpha))
                self.display_surface.blit(flash_surface, (0, 0))
                self.impact_flash_alpha = int(self.impact_flash_alpha * self.flash_decay)

            current_time = time.time()
            marks_to_keep = []
            for mark in self.slap_marks:
                age = current_time - mark["timestamp"]
                if age < self.mark_lifetime:
                    age_ratio = age / self.mark_lifetime
                    mark_alpha = int(255 * (1.0 - age_ratio))
                    mark_surface = pygame.Surface((mark["size"] * 2, mark["size"] * 2), pygame.SRCALPHA)
                    pygame.draw.circle(
                        mark_surface,
                        (255, 100, 100, mark_alpha),
                        (mark["size"], mark["size"]),
                        mark["size"],
                        3,
                    )
                    self.display_surface.blit(
                        mark_surface,
                        (mark["x"] - mark["size"], mark["y"] - mark["size"]),
                    )
                    marks_to_keep.append(mark)
            self.slap_marks = marks_to_keep

            text_to_keep = []
            for entry in self.comic_texts:
                age = current_time - entry["timestamp"]
                if age < 0.8:
                    text_surface = pygame.font.SysFont("Segoe UI Black", 48).render(entry["text"], True, (255, 255, 255))
                    self.display_surface.blit(text_surface, (entry["x"], entry["y"] - int(age * 20)))
                    text_to_keep.append(entry)
            self.comic_texts = text_to_keep

            confetti_to_keep = []
            for particle in self.confetti_particles:
                age = current_time - particle["timestamp"]
                if age < 1.2:
                    particle["x"] += particle["vx"]
                    particle["y"] += particle["vy"]
                    particle["vy"] += 0.2
                    color = (255, 215, 0, max(0, 255 - int(age * 220)))
                    surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                    surf.fill(color)
                    self.display_surface.blit(surf, (particle["x"], particle["y"]))
                    confetti_to_keep.append(particle)
            self.confetti_particles = confetti_to_keep

            cracks_to_keep = []
            for crack in self.glass_cracks:
                age = current_time - crack["timestamp"]
                if age < 2.5:
                    alpha = max(0, 150 - int(age * 50))
                    overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                    pygame.draw.line(overlay, (220, 220, 220, alpha), (0, 0), (self.screen_width, self.screen_height), 2)
                    pygame.draw.line(overlay, (220, 220, 220, alpha), (self.screen_width, 0), (0, self.screen_height), 2)
                    self.display_surface.blit(overlay, (0, 0))
                    cracks_to_keep.append(crack)
            self.glass_cracks = cracks_to_keep

            pygame.display.flip()
            self.clock.tick(60)

    def cleanup(self) -> None:
        self.running = False
        if self.effects_thread and self.effects_thread.is_alive():
            self.effects_thread.join(timeout=1.0)
        self._shutdown_display()
        self.logger.info("Visual effects cleaned up")


class VisualEffectsService:
    """Singleton wrapper around the visual effects engine."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        self._effects: Optional[VisualEffects] = None
        self.options = {
            "screen_flash": True,
            "screen_shake": True,
            "comic_text": True,
            "glass_crack": False,
            "confetti": False,
            "disable_effects": False,
        }

    def init(self) -> Optional[VisualEffects]:
        if self._effects is None:
            self._effects = VisualEffects(self.logger)
        return self._effects

    def trigger(self, force_ratio: float, position: Optional[Tuple[int, int]] = None) -> None:
        effects = self._effects or self.init()
        if not effects:
            return
        effects.update_options(self.options)
        try:
            effects.trigger_slap_effect(force_ratio, position)
        except Exception:
            self.options["disable_effects"] = True
            effects.cleanup()
            self._effects = None
            self.logger.exception("Visual effects failed during trigger and were disabled")

    def cleanup(self) -> None:
        if self._effects:
            self._effects.cleanup()
            self._effects = None

    def update_options(self, options) -> None:
        self.options.update(options)


_default_service: Optional[VisualEffectsService] = None


def _get_default_service(logger: Optional[logging.Logger] = None) -> VisualEffectsService:
    global _default_service
    if _default_service is None:
        _default_service = VisualEffectsService(logger or logging.getLogger("SlapPC"))
    return _default_service


def init_visual_effects(logger: Optional[logging.Logger] = None) -> VisualEffects:
    return _get_default_service(logger).init()


def trigger_slap_effect(
    force_ratio: float,
    position: Optional[Tuple[int, int]] = None,
    logger: Optional[logging.Logger] = None,
) -> None:
    _get_default_service(logger).trigger(force_ratio, position)


def cleanup_visual_effects(logger: Optional[logging.Logger] = None) -> None:
    global _default_service
    service = _default_service or _get_default_service(logger)
    service.cleanup()
    _default_service = None
