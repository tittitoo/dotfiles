# logind.conf.d overrides

Machine-wide systemd-logind settings. These live in
`/etc/systemd/logind.conf.d/`, which `stow` can't reach (outside `$HOME`),
so they're installed with `install.sh` instead — see `keyd/` for the same
pattern.

## 10-ignore-power-button.conf

By default, systemd-logind grabs the power button device exclusively and
acts on a press itself (e.g. suspend/poweroff) before Hyprland ever sees the
key event. Setting `HandlePowerKey=ignore` releases that grab, so the
physical power key reaches Hyprland as a normal `XF86PowerOff` key event and
can be bound like any other key.

That's what makes the power-key binding in `hypr/.config/hypr/bindings.lua`
(short press -> `omarchy-system-lock`, overriding Omarchy's default of
opening the power menu) work at all. Without this override, logind would
consume the key first and the Hyprland binding would never fire.

Long-press behavior is untouched: `HandlePowerKeyLongPress` stays at its
default (`ignore`), and holding the button long enough triggers the
laptop's own hardware/firmware force-shutoff, which happens below the OS
and can't be configured here.

## Applying after install

```
sudo cp 10-ignore-power-button.conf /etc/systemd/logind.conf.d/
sudo systemctl restart systemd-logind
```

Restarting `systemd-logind` is safe and does not end your session (session
state is tracked separately, not by the logind process's uptime).
