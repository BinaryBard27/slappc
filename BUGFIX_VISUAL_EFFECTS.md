# BUGFIX: Visual Effects Overlay Could Cover the Desktop

## Root Cause

The visual effects system created a fullscreen, topmost Pygame window during startup. That window was intended to be transparent and click-through, but initialization was not transactional.

If startup failed after `pygame.display.set_mode(...)` succeeded, the code only logged the error and returned. In that path, the overlay window could remain alive, leaving the desktop invisible or covered by a fullscreen surface.

The risky paths were:

- fullscreen overlay creation in `effects.py`
- click-through / layered window setup on Windows
- `always on top` handling via `HWND_TOPMOST`
- partial initialization failures that did not tear the window down

## Fix

The overlay lifecycle is now cleaned up safely when initialization fails:

- overlay setup is treated as transactional
- partially created displays are destroyed immediately on failure
- the code now tears down the Pygame display and, when appropriate, quits Pygame itself
- Windows click-through configuration now fails closed instead of leaving a potentially visible overlay behind

## Safety Fallback

If visual effects fail to initialize at startup, the app now disables visual effects by default for that run and persists `disable_effects = true` to config.

That keeps the main app usable instead of risking a fullscreen overlay over the desktop.

## Behavior Preserved

- The visual effects feature still exists.
- Successful startup still enables flash, shake, comic text, and optional glass crack/confetti effects.
- Cleanup still shuts down the overlay normally during app exit.

## Files Changed

- `effects.py`
- `app.py`

