# Performance Report

## Current Performance Characteristics

- Microphone processing is still lightweight and callback-driven.
- Detection uses simple array math and a small amount of state.
- Pack discovery is filesystem-based and re-evaluated on demand.
- Sound playback creates a `pygame.mixer.Sound` object per play event.
- Visual effects render continuously while active.
- Stats and config writes happen synchronously.

## Safe Optimizations Already Applied

- Removed redundant runtime layers that were not used.
- Eliminated duplicate shutdown execution.
- Prevented duplicate USB listener threads.
- Fixed the detector scale mismatch so calibration and peak gating are meaningful.
- Added delayed log file creation to avoid unnecessary file handles during import.

## Remaining Performance Risks

- Repeated pack discovery on every sound playback is acceptable for this app size, but not ideal.
- Per-event sound loading adds overhead if slap frequency becomes high.
- Visual effects use `pygame` surfaces every frame while active.
- Synchronous stats/config writes still occur in the hot path.
- The detector still runs in the audio callback thread, so expensive future logic would need careful isolation.

## Practical Assessment

The app is fast enough for its intended desktop workload, but it is not yet tuned for high-event-rate usage. The main remaining bottlenecks are architectural rather than algorithmic.

