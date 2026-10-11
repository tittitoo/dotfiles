# modprobe config

Machine-specific kernel module parameters. These live in `/etc/modprobe.d/`,
which `stow` can't reach (outside `$HOME`), so they're installed with
`install.sh` instead - see `udev/` and `keyd/` for the same pattern.

## What it does

Disables `btusb`'s built-in runtime-PM autosuspend
(`enable_autosuspend=0`). This is separate from, and sits below, the
generic USB `power/control` sysfs attribute that
`udev/99-starlite-bluetooth-no-autosuspend.rules` forces to `on` - that
rule alone did not stop the Intel AX200/201-class Bluetooth controller
(hci0) from intermittently crashing with `Hardware error 0x0c` (dropping
the Toucan keyboard's BLE connection), because `enable_autosuspend` stayed
`Y` the whole time regardless of the udev rule's effect.

## Setting up on a (new) machine

```
./install.sh
```

Installs the modprobe.d file (takes effect on next module load/boot) and
also flips the parameter live via sysfs, so no reboot is needed to confirm
the fix.

Check it's active:

```
cat /sys/module/btusb/parameters/enable_autosuspend   # should print N
```
