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

## 99-starlite-bluetooth-no-autosuspend.rules

StarLite laptop, Intel AX200/201-class Bluetooth controller (USB
`8087:0aaa`).

On resume from suspend, this controller's firmware intermittently crashes
(`kernel: Bluetooth: hci0: Hardware error 0x0c`), forcing a full reset of
the Bluetooth stack and dropping any connected devices — most visibly the
Toucan keyboard, which shows up as a flaky/intermittent Bluetooth
reconnect right after waking the laptop. This is triggered by USB
autosuspend on the controller kicking in while a BLE peripheral is
actively reconnecting and hammering it with GATT traffic right after
wake.

This rule sets the USB power control policy to `on` (i.e. disables
autosuspend) for just this device, which avoids the crash.
