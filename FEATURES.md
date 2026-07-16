# SlapPC 2.0 Features

## Current Architecture

- `slappc.py` remains the startup entrypoint
- `app.py` orchestrates the runtime
- `config.py` owns config persistence and validation
- `packs.py` discovers both manifest-based and legacy sound packs
- `detector.py` provides improved slap detection
- `audio.py` handles playback and microphone capture
- `tray.py` manages system tray actions
- `ui.py` provides the modern settings window
- `effects.py` manages optional visual effects
- `stats.py` persists usage statistics and achievements

## Implemented Features

- CustomTkinter dark settings window with live microphone meter
- sensitivity slider
- output volume slider
- detection enable/disable toggle
- test sound button
- sound pack selector
- launch at startup toggle
- minimize to tray toggle
- restore defaults
- plugin-style sound pack discovery
- manifest-based pack metadata
- improved slap detection with calibration and peak gating
- persistent statistics storage
- daily history tracking
- achievement unlocks and popups
- optional visual effects:
  - screen flash
  - screen shake
  - comic impact text
  - fake glass crack overlay
  - confetti
  - disable all effects
- logging and validation improvements
- unit tests for config, detector, and pack manager

## Backward Compatibility

- existing `config.json` files are still supported
- legacy `sounds/pack_*` folders are still discovered
- the app still starts from `slappc.py`
- the old `visual_effects.py` import path remains available

## Pack Format

New packs can live in `packs/<PackName>/` with a `manifest.json` file:

```json
{
  "name": "Default",
  "author": "SlapPC",
  "version": "2.0",
  "description": "Default bundled slap pack",
  "volume": 1.0
}
```

The pack folder may contain `.wav` clips such as `slap1.wav` and `slap2.wav`.

