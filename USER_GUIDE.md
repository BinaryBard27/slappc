# SlapPC 2.0 User Guide

## Starting The App

- Run `python slappc.py`
- Or launch the packaged EXE on Windows

## Using The Settings Window

- Open the tray menu and choose `Settings`
- Adjust sensitivity and output volume
- Enable or disable detection
- Choose a sound pack
- Toggle launch at startup
- Toggle minimize to tray
- Choose which visual effects are enabled
- Use `Test Sound` to preview the active pack
- Use `Calibration Wizard` to calibrate ambient noise
- Use `Restore Defaults` to reset settings
- Click `Save` to apply changes

## Sound Packs

- Legacy packs under `sounds/pack_*` still work
- New plugin-style packs belong in `packs/<PackName>/`
- Each new pack should include a `manifest.json`
- You can switch packs without restarting

## Statistics

- SlapPC tracks lifetime slaps
- It also tracks today's slaps, strongest slap, average force, sessions, and daily history
- Statistics are stored locally

## Achievements

Unlocked achievements are shown as popups:

- First Slap
- 10 Slaps
- 100 Slaps
- 1000 Slaps
- Maximum Force
- One Hour Session

## Visual Effects

You can turn each effect on or off:

- screen flash
- screen shake
- comic impact text
- fake glass crack overlay
- confetti
- disable all effects

## Compatibility Notes

- Existing config files are still read
- Existing sound folders still work
- `slappc.py` remains the supported entrypoint

