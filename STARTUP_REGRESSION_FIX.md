# Startup Regression Fix

## Root Cause

The desktop blackout was caused by the visual effects system creating its overlay too early during application startup.

The offending path was:

- `effects.py` in `VisualEffects.__init__()`
- called indirectly from `app.py` in `SlapPCApp.run()`

`VisualEffects.__init__()` immediately initialized Pygame display state and created a fullscreen `pygame.display.set_mode(...)` window with `NOFRAME`, `SRCALPHA`, and Windows topmost / layered / transparent configuration.

That meant the app could cover the desktop before any slap event occurred.

## Exact File

- [`D:\slappc\effects.py`](D:\slappc\effects.py)
- [`D:\slappc\app.py`](D:\slappc\app.py)

## Exact Functions

- `VisualEffects.__init__()`
- `VisualEffects._init_display()`
- `VisualEffects.trigger_slap_effect()`
- `VisualEffectsService.init()`
- `SlapPCApp.run()`

## Why It Happened

The effects system mixed two responsibilities:

- internal state setup
- window creation

Because the constructor opened the overlay immediately, startup code triggered a fullscreen, always-on-top window before any user action.

## How It Was Fixed

The startup path was changed so no overlay window is created during app launch:

- `VisualEffects.__init__()` now only prepares internal state
- `VisualEffects._init_display()` is called lazily from `VisualEffects.trigger_slap_effect()` on the first slap
- `SlapPCApp.run()` no longer initializes the effects window at startup
- if overlay creation fails at first use, visual effects are automatically disabled instead of affecting the desktop

## Result

- Startup no longer creates a fullscreen overlay
- Visual effects still exist
- The overlay is created only when the first slap event happens
- Failed overlay initialization now fails closed by disabling visual effects

