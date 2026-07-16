# Changelog

## 2.0.0

### Added

- CustomTkinter-based dark settings window
- live microphone meter
- manifest-based plugin sound pack system
- improved slap detector with calibration and peak gating
- persistent statistics and daily history
- achievements with popup notifications
- optional visual effects with per-effect toggles
- config validation
- logging improvements
- unit tests for core services

### Changed

- app startup is now routed through a modular service layer
- sound pack discovery supports both new `packs/` plugins and legacy `sounds/` folders
- the old `visual_effects.py` path remains as a compatibility wrapper

### Compatibility

- `config.json` compatibility preserved
- `slappc.py` remains the entrypoint
- legacy sound packs still work

