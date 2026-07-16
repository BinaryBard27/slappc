"""Application orchestration for SlapPC 2.0."""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from audio import MicListener, SoundPlayer
from config import ConfigStore
from detector import SlapDetector
from effects import VisualEffectsService
from logger import configure_logging
from packs import PackManager
from stats import StatisticsStore
from tray import TrayController
from ui import open_settings_window


class SlapPCApp:
    """Coordinate startup, runtime services, and shutdown."""

    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parent
        self.sounds_dir = str(self.base_dir / "sounds")
        self.assets_dir = str(self.base_dir / "assets")
        self.config_file = str(self.base_dir / "config.json")
        self.stats_file = str(self.base_dir / "stats.json")
        self.logger = configure_logging(str(self.base_dir))
        self.config_store = ConfigStore(self.config_file, self.logger)
        self.pack_manager = PackManager(self.logger)
        self.detector = SlapDetector(self.logger)
        self.effects_service = VisualEffectsService(self.logger)
        self.sound_player = SoundPlayer(self.pack_manager, self.config_store.data, self.logger)
        self.stats_store = StatisticsStore(self.stats_file, self.logger)
        self.mic_listener = MicListener(
            self.config_store.data,
            self.detector,
            self.sound_player,
            self._trigger_effect,
            self._record_slap,
            self.logger,
        )
        self.tray = TrayController(
            self.assets_dir,
            self.pack_manager,
            self.config_store.data,
            self.logger,
            self._open_settings_window,
            self.start_usb_moaner,
            self.stop,
            self.restore_defaults,
        )
        self._stopped = False
        self._usb_listener_started = False

    def _record_slap(self, force_ratio: float) -> None:
        unlocked = self.stats_store.record_slap(force_ratio)
        self.config_store.data["slap_count"] = self.stats_store.lifetime_slaps
        self.config_store.save()
        self.tray.update_title()
        if unlocked:
            self.tray.notify("Achievement Unlocked", "\n".join(unlocked))

    def _trigger_effect(self, force_ratio: float) -> None:
        self.effects_service.trigger(force_ratio)

    def _open_settings_window(self) -> None:
        open_settings_window(
            self.config_store.data,
            self.pack_manager,
            self.config_store.save,
            self.set_launch_at_login,
            self.effects_service.update_options,
            self.detector.calibrate_start,
            self.sound_player.play_slap_sound,
            self.tray.update_title,
            lambda: self.mic_listener.last_meter_value,
            self.logger,
        )

    def set_launch_at_login(self, enabled: bool) -> None:
        if sys.platform != "win32":
            return
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            if enabled:
                winreg.SetValueEx(key, "SlapPC", 0, winreg.REG_SZ, sys.executable)
            else:
                try:
                    winreg.DeleteValue(key, "SlapPC")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            self.logger.exception("Launch at startup update failed")

    def start_usb_moaner(self) -> None:
        if sys.platform != "win32":
            self.logger.info("USB moaner skipped on non-Windows platform")
            return
        if self._usb_listener_started:
            return
        self._usb_listener_started = True
        try:
            import win32con
            import win32gui

            def wnd_proc(hwnd, msg, wparam, lparam):
                if msg == win32con.WM_DEVICECHANGE and wparam in (0x8000, 0x8004):
                    self.logger.info("USB event detected")
                    threading.Thread(
                        target=self.sound_player.play_slap_sound,
                        args=(0.7,),
                        daemon=True,
                    ).start()
                return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = wnd_proc
            wc.lpszClassName = "SlapPCUSBListener"
            win32gui.RegisterClass(wc)
            win32gui.CreateWindow(wc.lpszClassName, "", 0, 0, 0, 0, 0, 0, 0, None, None)

            while self.config_store.data["usb_moaner"] and self.mic_listener.is_running:
                win32gui.PumpWaitingMessages()
                import time

                time.sleep(0.1)
        except ImportError:
            self.logger.warning("pywin32 not installed; USB moaner disabled")
        except Exception:
            self.logger.exception("USB moaner failed")
        finally:
            self._usb_listener_started = False

    def restore_defaults(self) -> None:
        self.config_store.reset_defaults()
        self.config_store.save()
        self.set_launch_at_login(False)
        self.effects_service.update_options(self.config_store.data)
        self.tray.update_title()

    def run(self) -> None:
        self.logger.info("Starting SlapPC 2.0")
        self.config_store.load()
        self.config_store.validate()
        self.stats_store.load()
        self.config_store.data["slap_count"] = int(self.stats_store.lifetime_slaps or self.config_store.data["slap_count"])
        self.effects_service.update_options(self.config_store.data)

        mic_thread = threading.Thread(target=self.mic_listener.start, daemon=True)
        mic_thread.start()
        if self.config_store.data.get("usb_moaner"):
            threading.Thread(target=self.start_usb_moaner, daemon=True).start()

        tray_icon = self.tray.build()
        try:
            tray_icon.run()
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop background services and finalize shutdown."""
        if self._stopped:
            return
        self._stopped = True
        self.mic_listener.is_running = False
        self.stats_store.end_session()
        self.effects_service.cleanup()
        self.logger.info("SlapPC shutdown complete")


def main() -> None:
    """Entry point used by the wrapper script and packaged build."""
    SlapPCApp().run()


if __name__ == "__main__":
    main()
