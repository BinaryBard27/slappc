# Bug Report

## Fixed During Review

- `Restore Defaults` in the settings window updated widgets but did not persist or apply the defaults to the running app.
- Old config booleans could be misread because Python `bool("false")` evaluates to `True`.
- The detector peak gate used normalized peak values against raw RMS thresholds, so calibration could fail to detect obvious impacts.
- Shutdown was not idempotent; the tray quit path and `finally` block could both call cleanup, risking duplicate session writes.
- The USB listener could be started multiple times, creating duplicate background threads.
- Achievement popups were launched from a worker thread using a fresh Tk root, which is not safe for Tkinter.
- The legacy slap counter path could drift from the persisted stats store.
- Restore defaults did not disable launch-at-startup at the Windows registry level.
- `visual_effects.py` only re-exported helper functions before; class imports would have broken for downstream code.

## Remaining Issues

- The app still relies on shared mutable config across threads.
- Visual effects still render on a dedicated thread and are not fully synchronized.
- Sound pack discovery rescans the filesystem on demand, which is safe but not optimal.
- The settings window is live-updated, but there is still no automated UI integration test for CustomTkinter controls.
- Tray notification behavior may vary by platform and desktop environment.

## Verified Behavior

- `slappc.py` remains the entrypoint.
- Existing `config.json` values still load.
- Legacy `sounds/pack_*` folders still work.
- New `packs/Default/manifest.json` packs are discovered.
- Sound pack switching updates the active pack without restarting.
- Detector calibration completes and detection now triggers on an impact-like waveform.
- Statistics update on slap events and persist to `stats.json`.
- Achievements are recorded and surfaced through tray notifications.
- Visual effects can be toggled individually and disabled as a group.

