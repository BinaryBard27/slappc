# SlapPC

SlapPC is a Windows desktop app that listens to your microphone, detects slap-like impact spikes, and responds with configurable sound and visual feedback.

It is designed to be lightweight, tray-first, and easy to extend with custom sound packs and optional visual effects.

## Features

- Real-time microphone impact detection
- Volume-scaled slap sounds
- System tray controls
- Custom sound pack support
- Optional visual effects
- Startup and launch-at-login options
- Session and lifetime slap statistics

## Visual Effects

Visual effects are available, but they are intentionally lazy-loaded so the app does not create any overlay window during startup.

Supported effects include:

- screen flash
- screen shake
- comic impact text
- glass crack overlay
- confetti

If the overlay fails to initialize, visual effects are automatically disabled for safety instead of affecting the desktop.

## Quick Start

```bash
pip install -r requirements.txt
python slappc.py
```

A tray icon will appear after launch.

## Build for Windows

Use the bundled build script:

```bash
build.bat
```

This produces a packaged Windows executable in `dist/`.

## Sound Packs

Place `.wav` files into a folder under `sounds/pack_<name>/`.

Example:

```text
sounds/
  pack_scream/
    scream1.wav
    scream2.wav
  pack_goat/
    goat1.wav
```

The tray menu can switch between available packs at runtime.

## Configuration

Runtime settings are stored in `config.json`.

Common options include:

- sensitivity
- cooldown
- volume
- detection enabled
- minimize to tray
- launch at login
- visual effects toggles

## Project Structure

- `slappc.py` entrypoint
- `app.py` application orchestration
- `audio.py` microphone and sound playback
- `detector.py` slap detection logic
- `effects.py` visual effects engine
- `ui.py` settings window
- `tray.py` system tray integration
- `packs.py` sound pack discovery
- `stats.py` session and lifetime stats

## Recent Fixes

- Visual effects now initialize lazily and do not create a window during startup
- Failed overlay creation disables visual effects safely
- Startup overlay regressions are documented in `STARTUP_REGRESSION_FIX.md`
- Visual effects overlay cleanup and fallback behavior are documented in `BUGFIX_VISUAL_EFFECTS.md`

## Notes

This project is built for Windows.
Some optional features depend on `pywin32`.

