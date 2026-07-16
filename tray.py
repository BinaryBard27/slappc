"""System tray integration."""

from __future__ import annotations

import logging
import os
import threading
from typing import Callable

import pystray
from PIL import Image
from pystray import MenuItem as item


class TrayController:
    """Build and manage the system tray icon."""

    def __init__(
        self,
        assets_dir: str,
        pack_manager,
        config,
        logger: logging.Logger,
        open_settings_window: Callable[[], None],
        start_usb_moaner: Callable[[], None],
        on_quit: Callable[[], None],
        restore_defaults: Callable[[], None],
    ) -> None:
        self.assets_dir = assets_dir
        self.pack_manager = pack_manager
        self.config = config
        self.logger = logger
        self.open_settings_window = open_settings_window
        self.start_usb_moaner = start_usb_moaner
        self.on_quit = on_quit
        self.restore_defaults = restore_defaults
        self.icon = None

    def update_title(self) -> None:
        if self.icon:
            self.icon.title = f"SlapPC — {self.config['slap_count']} slaps"

    def _make_pack_menu(self):
        packs = self.pack_manager.discover()

        def make_setter(pack_name: str):
            def setter(icon, _item):
                self.config["sound_pack"] = pack_name
                self.logger.info("Sound pack changed to %s", pack_name)

            return setter

        return [
            item(pack.name, make_setter(pack.name), checked=lambda _i, p=pack: self.config["sound_pack"] == p.name)
            for pack in packs.values()
        ]

    def build(self):
        icon_path = os.path.join(self.assets_dir, "icon.png")
        img = Image.open(icon_path) if os.path.exists(icon_path) else Image.new("RGB", (64, 64), "red")

        def on_sensitivity_low(_icon, _menu_item):
            self.config["sensitivity"] = 0.1

        def on_sensitivity_mid(_icon, _menu_item):
            self.config["sensitivity"] = 0.35

        def on_sensitivity_high(_icon, _menu_item):
            self.config["sensitivity"] = 0.7

        def on_toggle_usb(_icon, _menu_item):
            self.config["usb_moaner"] = not self.config["usb_moaner"]
            if self.config["usb_moaner"]:
                threading.Thread(target=self.start_usb_moaner, daemon=True).start()

        def on_reset_counter(_icon, _menu_item):
            self.config["slap_count"] = 0
            self.update_title()

        def on_open_settings(_icon, _menu_item):
            threading.Thread(target=self.open_settings_window, daemon=True).start()

        def on_restore_defaults(_icon, _menu_item):
            self.restore_defaults()

        def on_quit(icon, _menu_item):
            self.on_quit()
            icon.stop()

        menu = pystray.Menu(
            item(f"SlapPC — {self.config['slap_count']} slaps", lambda *_a: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item("Settings", on_open_settings),
            pystray.Menu.SEPARATOR,
            item("Sound Pack", pystray.Menu(*self._make_pack_menu())),
            item(
                "Sensitivity",
                pystray.Menu(
                    item("Low (needs a real slap)", on_sensitivity_high, checked=lambda _i: self.config["sensitivity"] >= 0.6),
                    item("Medium (default)", on_sensitivity_mid, checked=lambda _i: 0.2 < self.config["sensitivity"] < 0.6),
                    item("High (light tap)", on_sensitivity_low, checked=lambda _i: self.config["sensitivity"] <= 0.2),
                ),
            ),
            pystray.Menu.SEPARATOR,
            item("USB Moaner", on_toggle_usb, checked=lambda _i: self.config["usb_moaner"]),
            pystray.Menu.SEPARATOR,
            item("Reset Slap Counter", on_reset_counter),
            item("Restore Defaults", on_restore_defaults),
            item("Quit SlapPC", on_quit),
        )

        self.icon = pystray.Icon(
            "SlapPC",
            img,
            f"SlapPC — {self.config['slap_count']} slaps",
            menu,
        )
        return self.icon

    def notify(self, title: str, message: str) -> None:
        """Send a tray notification if the icon is available."""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception:
                self.logger.exception("Tray notification failed")
        else:
            self.logger.info("%s: %s", title, message)
