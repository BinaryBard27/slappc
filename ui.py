"""Modern CustomTkinter settings window."""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict

try:
    import customtkinter as ctk
except Exception:  # pragma: no cover - fallback only
    ctk = None


class SettingsWindow:
    """Modern dark settings UI with a live input meter."""

    def __init__(
        self,
        config,
        pack_manager,
        save_config: Callable[[], None],
        set_launch_at_login: Callable[[bool], None],
        update_effect_options: Callable[[Dict[str, bool]], None],
        calibrate_detector: Callable[[int], None],
        test_sound: Callable[[], None],
        update_tray_title: Callable[[], None],
        logger: logging.Logger,
    ) -> None:
        self.config = config
        self.pack_manager = pack_manager
        self.save_config = save_config
        self.set_launch_at_login = set_launch_at_login
        self.update_effect_options = update_effect_options
        self.calibrate_detector = calibrate_detector
        self.test_sound = test_sound
        self.update_tray_title = update_tray_title
        self.logger = logger
        self.root = None
        self._traces_bound = False

    def show(self, meter_source: Callable[[], float]) -> None:
        """Open the settings UI."""
        if ctk is not None:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("dark-blue")
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()
            self.root.configure(bg="#121212")
        self.root.title("SlapPC 2.0 Settings")
        self.root.geometry("560x720")
        self.root.minsize(520, 680)

        self._build_ui(meter_source)
        self._start_meter_poll(meter_source)
        self.root.mainloop()

    def _widget(self, cls_name: str):
        return getattr(ctk, cls_name) if ctk is not None else getattr(tk, cls_name)

    def _build_ui(self, meter_source: Callable[[], float]) -> None:
        main = self._widget("CTkFrame")(self.root) if ctk is not None else tk.Frame(self.root, bg="#121212")
        main.pack(fill="both", expand=True, padx=18, pady=18)

        title = self._widget("CTkLabel")(main, text="SlapPC 2.0", font=("Segoe UI", 24, "bold"))
        title.pack(pady=(0, 8))
        subtitle = self._widget("CTkLabel")(main, text="Modern slap detection and tray controls", text_color="#A5A5A5")
        subtitle.pack(pady=(0, 12))

        meter_label = self._widget("CTkLabel")(main, text="Live Microphone Meter")
        meter_label.pack(anchor="w", pady=(8, 2))
        self.meter_progress = self._widget("CTkProgressBar")(main)
        self.meter_progress.set(0.0)
        self.meter_progress.pack(fill="x", pady=(0, 14))

        self.sensitivity = tk.DoubleVar(value=self.config["sensitivity"])
        self.volume = tk.DoubleVar(value=self.config["volume"])
        self.detection_enabled = tk.BooleanVar(value=self.config.get("detection_enabled", True))
        self.launch_at_startup = tk.BooleanVar(value=self.config.get("launch_at_login", False))
        self.minimize_to_tray = tk.BooleanVar(value=self.config.get("minimize_to_tray", True))
        self.sound_pack = tk.StringVar(value=self.config["sound_pack"])

        self.screen_flash = tk.BooleanVar(value=self.config.get("screen_flash", True))
        self.screen_shake = tk.BooleanVar(value=self.config.get("screen_shake", True))
        self.comic_text = tk.BooleanVar(value=self.config.get("comic_text", True))
        self.glass_crack = tk.BooleanVar(value=self.config.get("glass_crack", False))
        self.confetti = tk.BooleanVar(value=self.config.get("confetti", False))
        self.disable_effects = tk.BooleanVar(value=self.config.get("disable_effects", False))

        self._add_slider(main, "Sensitivity", self.sensitivity, 0.0, 1.0)
        self._add_slider(main, "Output Volume", self.volume, 0.0, 1.0)

        self._add_checkbox(main, "Enable/Disable Detection", self.detection_enabled)
        self._add_checkbox(main, "Launch at startup", self.launch_at_startup)
        self._add_checkbox(main, "Minimize to tray", self.minimize_to_tray)

        self._add_selector(main)
        self._add_effects_section(main)
        self._bind_live_updates()

        btn_row = self._widget("CTkFrame")(main) if ctk is not None else tk.Frame(main, bg="#121212")
        btn_row.pack(fill="x", pady=(10, 6))
        self._button(btn_row, "Test Sound", lambda: self.test_sound(0.7)).pack(side="left", expand=True, fill="x", padx=4)
        self._button(btn_row, "Calibration Wizard", self._start_calibration).pack(side="left", expand=True, fill="x", padx=4)

        save_row = self._widget("CTkFrame")(main) if ctk is not None else tk.Frame(main, bg="#121212")
        save_row.pack(fill="x", pady=(10, 4))
        self._button(save_row, "Restore Defaults", self._restore_defaults).pack(side="left", expand=True, fill="x", padx=4)
        self._button(save_row, "Save", self._save).pack(side="left", expand=True, fill="x", padx=4)

    def _button(self, parent, text: str, command: Callable[[], None]):
        if ctk is not None:
            return ctk.CTkButton(parent, text=text, command=command)
        return tk.Button(parent, text=text, command=command)

    def _label(self, parent, text: str):
        if ctk is not None:
            return ctk.CTkLabel(parent, text=text)
        return tk.Label(parent, text=text, fg="white", bg="#121212")

    def _add_slider(self, parent, label: str, var, minimum: float, maximum: float) -> None:
        self._label(parent, label).pack(anchor="w", pady=(8, 2))
        if ctk is not None:
            ctk.CTkSlider(parent, from_=minimum, to=maximum, variable=var).pack(fill="x")
        else:
            tk.Scale(parent, from_=minimum, to=maximum, orient=tk.HORIZONTAL, variable=var, resolution=0.01).pack(fill="x")

    def _add_checkbox(self, parent, text: str, var) -> None:
        if ctk is not None:
            ctk.CTkCheckBox(parent, text=text, variable=var).pack(anchor="w", pady=2)
        else:
            tk.Checkbutton(parent, text=text, variable=var, bg="#121212", fg="white").pack(anchor="w", pady=2)

    def _add_selector(self, parent) -> None:
        self._label(parent, "Sound Pack Selector").pack(anchor="w", pady=(10, 2))
        options = list(self.pack_manager.discover().keys())
        if ctk is not None:
            ctk.CTkOptionMenu(parent, values=options, variable=self.sound_pack).pack(fill="x")
        else:
            tk.OptionMenu(parent, self.sound_pack, *options).pack(fill="x")

    def _add_effects_section(self, parent) -> None:
        self._label(parent, "Visual Effects").pack(anchor="w", pady=(10, 2))
        for text, var in [
            ("Screen flash", self.screen_flash),
            ("Screen shake", self.screen_shake),
            ("Comic impact text", self.comic_text),
            ("Fake glass crack overlay", self.glass_crack),
            ("Confetti", self.confetti),
            ("Disable all effects", self.disable_effects),
        ]:
            self._add_checkbox(parent, text, var)

    def _bind_live_updates(self) -> None:
        if self._traces_bound:
            return

        def sync_config(*_args) -> None:
            self.config["sensitivity"] = float(self.sensitivity.get())
            self.config["volume"] = float(self.volume.get())
            self.config["detection_enabled"] = bool(self.detection_enabled.get())
            self.config["launch_at_login"] = bool(self.launch_at_startup.get())
            self.config["minimize_to_tray"] = bool(self.minimize_to_tray.get())
            self.config["sound_pack"] = self.sound_pack.get()
            self.config["screen_flash"] = bool(self.screen_flash.get())
            self.config["screen_shake"] = bool(self.screen_shake.get())
            self.config["comic_text"] = bool(self.comic_text.get())
            self.config["glass_crack"] = bool(self.glass_crack.get())
            self.config["confetti"] = bool(self.confetti.get())
            self.config["disable_effects"] = bool(self.disable_effects.get())
            self.set_launch_at_login(self.config["launch_at_login"])
            self.update_effect_options(
                {
                    "screen_flash": self.config["screen_flash"],
                    "screen_shake": self.config["screen_shake"],
                    "comic_text": self.config["comic_text"],
                    "glass_crack": self.config["glass_crack"],
                    "confetti": self.config["confetti"],
                    "disable_effects": self.config["disable_effects"],
                }
            )

        for var in (
            self.sensitivity,
            self.volume,
            self.detection_enabled,
            self.launch_at_startup,
            self.minimize_to_tray,
            self.sound_pack,
            self.screen_flash,
            self.screen_shake,
            self.comic_text,
            self.glass_crack,
            self.confetti,
            self.disable_effects,
        ):
            var.trace_add("write", sync_config)
        self._traces_bound = True

    def _start_meter_poll(self, meter_source: Callable[[], float]) -> None:
        def tick() -> None:
            if not self.root:
                return
            meter = min(1.0, max(0.0, meter_source()))
            self.meter_progress.set(meter)
            self.root.after(50, tick)

        tick()

    def _save(self) -> None:
        self.config["sensitivity"] = float(self.sensitivity.get())
        self.config["volume"] = float(self.volume.get())
        self.config["detection_enabled"] = bool(self.detection_enabled.get())
        self.config["launch_at_login"] = bool(self.launch_at_startup.get())
        self.config["minimize_to_tray"] = bool(self.minimize_to_tray.get())
        self.config["sound_pack"] = self.sound_pack.get()
        self.config["screen_flash"] = bool(self.screen_flash.get())
        self.config["screen_shake"] = bool(self.screen_shake.get())
        self.config["comic_text"] = bool(self.comic_text.get())
        self.config["glass_crack"] = bool(self.glass_crack.get())
        self.config["confetti"] = bool(self.confetti.get())
        self.config["disable_effects"] = bool(self.disable_effects.get())
        self.save_config()
        self.set_launch_at_login(self.config["launch_at_login"])
        self.update_effect_options(
            {
                "screen_flash": self.config["screen_flash"],
                "screen_shake": self.config["screen_shake"],
                "comic_text": self.config["comic_text"],
                "glass_crack": self.config["glass_crack"],
                "confetti": self.config["confetti"],
                "disable_effects": self.config["disable_effects"],
            }
        )
        self.update_tray_title()
        self.root.destroy()

    def _restore_defaults(self) -> None:
        self.config.update(
            {
                "sensitivity": 0.35,
                "volume": 1.0,
                "detection_enabled": True,
                "launch_at_login": False,
                "minimize_to_tray": True,
                "sound_pack": "Default",
                "screen_flash": True,
                "screen_shake": True,
                "comic_text": True,
                "glass_crack": False,
                "confetti": False,
                "disable_effects": False,
            }
        )
        self.sensitivity.set(0.35)
        self.volume.set(1.0)
        self.detection_enabled.set(True)
        self.launch_at_startup.set(False)
        self.minimize_to_tray.set(True)
        self.sound_pack.set("Default")
        self.screen_flash.set(True)
        self.screen_shake.set(True)
        self.comic_text.set(True)
        self.glass_crack.set(False)
        self.confetti.set(False)
        self.disable_effects.set(False)
        self.save_config()
        self.set_launch_at_login(False)
        self.update_effect_options(
            {
                "screen_flash": True,
                "screen_shake": True,
                "comic_text": True,
                "glass_crack": False,
                "confetti": False,
                "disable_effects": False,
            }
        )
        self.update_tray_title()

    def _start_calibration(self) -> None:
        self.calibrate_detector(40)
        messagebox.showinfo("Calibration", "Ambient calibration started. Tap away when prompted.")


def open_settings_window(
    config,
    pack_manager,
    save_config: Callable[[], None],
    set_launch_at_login: Callable[[bool], None],
    update_effect_options: Callable[[Dict[str, bool]], None],
    calibrate_detector: Callable[[int], None],
    test_sound: Callable[[], None],
    update_tray_title: Callable[[], None],
    meter_source: Callable[[], float],
    logger: logging.Logger,
) -> None:
    """Open the modern settings window."""
    try:
        window = SettingsWindow(
            config=config,
            pack_manager=pack_manager,
            save_config=save_config,
            set_launch_at_login=set_launch_at_login,
            update_effect_options=update_effect_options,
            calibrate_detector=calibrate_detector,
            test_sound=test_sound,
            update_tray_title=update_tray_title,
            logger=logger,
        )
        window.show(meter_source)
    except Exception:
        logger.exception("Failed to open settings window")
