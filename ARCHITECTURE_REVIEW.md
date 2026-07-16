# SlapPC Architecture Review

## Current Architecture

SlapPC is now organized as a small service-oriented desktop app with a thin compatibility entrypoint.

Runtime flow:

- [`slappc.py`](./slappc.py) imports and calls [`app.main()`](./app.py)
- [`app.py`](./app.py) orchestrates config, audio, detection, tray, settings, and visual effects
- [`config.py`](./config.py) owns JSON persistence and shared constants
- [`audio.py`](./audio.py) handles playback and microphone capture
- [`effects.py`](./effects.py) manages the overlay feedback system
- [`tray.py`](./tray.py) builds the system tray UI
- [`ui.py`](./ui.py) opens the Tkinter settings window
- [`packs.py`](./packs.py) discovers sound packs and WAV clips
- [`stats.py`](./stats.py) tracks slap count state
- [`logger.py`](./logger.py) configures logging

The old [`visual_effects.py`](./visual_effects.py) import path remains as a compatibility wrapper.

## Entry Point

The user-facing entry point is still [`slappc.py`](./slappc.py), which preserves the original startup command and packaged EXE behavior.

The actual orchestration entry point is [`app.main()`](./app.py).

## Component Responsibilities

### [`app.py`](./app.py)

- constructs the app
- wires services together
- starts microphone capture
- starts the tray icon
- handles shutdown

### [`config.py`](./config.py)

- stores defaults
- loads and saves `config.json`
- exposes shared audio constants

### [`audio.py`](./audio.py)

- initializes `pygame.mixer`
- selects random WAV clips
- plays slap sounds
- computes RMS from microphone data
- decides when a slap has happened

### [`effects.py`](./effects.py)

- initializes the transparent overlay
- makes it click-through on Windows
- renders screen shake, flash, and slap marks
- exposes a singleton compatibility service

### [`tray.py`](./tray.py)

- loads the tray icon image
- builds tray menus
- handles sensitivity, sound pack, USB, reset, settings, and quit actions

### [`ui.py`](./ui.py)

- renders the Tkinter settings window
- saves settings back to config
- applies login and USB changes

### [`packs.py`](./packs.py)

- lists available pack folders
- lists `.wav` files inside a selected pack

### [`stats.py`](./stats.py)

- holds the slap counter as a small state object

### [`logger.py`](./logger.py)

- configures log file and console output

## How Slap Detection Works

The detector remains RMS-based and intentionally simple:

1. `sounddevice.InputStream` opens the microphone.
2. Each callback computes RMS amplitude of the current buffer.
3. A rolling ambient baseline is updated.
4. Threshold is derived from ambient level and sensitivity.
5. If amplitude exceeds the threshold and cooldown has expired, the slap count increments.
6. A random sound clip and a visual effect are triggered asynchronously.

This preserves the original behavior:

- lower sensitivity value means more sensitive detection
- every slap increments the persisted slap counter
- sound and visual responses happen on background threads

## How Audio Playback Works

Audio playback still uses `pygame.mixer`.

Behavior:

- active pack is read from config
- a random `.wav` file is chosen from that pack
- clip volume is scaled by slap force and user volume
- playback is started on a daemon thread so the microphone callback stays responsive

## How Tray Integration Works

Tray behavior is preserved:

- tray icon comes from `assets/icon.png` or a fallback red square
- tray title shows the current slap count
- menu contains settings, sound packs, sensitivity presets, USB moaner, reset, and quit
- menu state reflects current config values
- quit stops the tray and shuts down background services

## How Settings And Config Work

Settings are still stored in `config.json`.

Persisted keys:

- `sensitivity`
- `cooldown`
- `sound_pack`
- `volume`
- `usb_moaner`
- `launch_at_login`
- `slap_count`

Loading behavior:

- defaults are applied first
- saved JSON is merged into the live config
- malformed config falls back to defaults with logged error handling

Saving behavior:

- tray actions and settings UI mutate the same in-memory config
- saves write the whole JSON file back to disk

## Dependencies

Runtime:

- `sounddevice`
- `numpy`
- `pygame`
- `pystray`
- `pillow`
- `pywin32` on Windows

Build-time:

- `pyinstaller`

Standard library:

- `json`
- `logging`
- `pathlib`
- `threading`
- `time`
- `random`
- `sys`
- `tkinter`
- `dataclasses`

## Dead Code

The most obvious dead or near-dead code was reduced during the refactor, but a few low-value items remain:

- compatibility wrapper [`visual_effects.py`](./visual_effects.py)
- one-off sound generation scripts in [`generate_sounds.py`](./generate_sounds.py) and [`generate_meme_sounds.py`](./generate_meme_sounds.py)
- the new [`stats.py`](./stats.py) is intentionally lightweight and could later be folded into a broader app state object

## Duplicated Code

Remaining duplication is intentionally small:

- both tray and settings UI still expose the same settings fields
- both are valid user entry points into the same configuration data

## Global State

The biggest original globals were removed, but shared mutable config still exists by design because the app behavior depends on one live state object being visible to tray, UI, audio, and effects.

That said, the architecture is now much cleaner:

- state is centralized in `ConfigStore`
- slap counter is separated into `SlapStats`
- mic and playback runtime state is separated into `AudioRuntime`
- visual overlay state is hidden behind `VisualEffectsService`

## Performance Notes

The main remaining performance concerns are the same as the original app design:

- synchronous config writes still happen when a slap is detected
- a new sound object is created for each play event
- overlay rendering is continuous while effects are active

These choices preserve behavior and keep the refactor conservative.

## Refactoring Roadmap

1. Add lightweight config validation and migration support
2. Cache loaded sound clips per pack
3. Introduce a background persistence queue for slap counter writes
4. Add explicit thread synchronization around shared app state
5. Replace the compatibility wrapper with the new module name only after downstream references are updated

Estimated difficulty:

- config validation: Small
- sound caching: Small to Medium
- async persistence queue: Medium
- thread synchronization: Medium
- wrapper removal: Small
