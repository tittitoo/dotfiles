# udev rules

Machine-specific udev rules that fix hardware misdetection. These live in
`/etc/udev/rules.d/`, which `stow` can't reach (outside `$HOME`), so they're
installed with `install.sh` instead — see `keyd/` for the same pattern.

## 99-starlite-touchscreen.rules

StarLite laptop, Goodix `GXTP7386:00 27C6:0111` touch digitizer.

The stock hwdb tags this device as a touchpad (`ID_INPUT_TOUCHPAD=1`)
instead of a touchscreen, even though it reports `INPUT_PROP_DIRECT`,
`BTN_TOUCH`, a full multitouch `ABS` axis set, and a physical size matching
the screen panel, not a touchpad. Because it looks like a touchpad but
doesn't behave like one, libinput logs "kernel bug: device failed touchpad
sanity checks" and drops the device entirely — the touchscreen doesn't work
at all until this is fixed.

This rule strips the bad `ID_INPUT_TOUCHPAD` tag and sets
`ID_INPUT_TOUCHSCREEN=1` instead, so libinput/Hyprland recognize it as
direct touch input.

Only matches the exact device name `GXTP7386:00 27C6:0111` (the plain touch
interface), not its `Stylus`/`Keyboard`/`UNKNOWN` sibling interfaces exposed
by the same chip, which are already tagged correctly.

**Note:** after installing or changing this rule, a running Hyprland session
won't pick it up until it's restarted (logout/login, or exit and relaunch
Hyprland) — libinput only classifies a device once, at compositor startup.
