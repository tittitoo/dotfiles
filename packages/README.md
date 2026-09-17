# Package manifests

Explicitly-installed package lists, per machine, so a fresh OS install can
restore everything instead of reinstalling from memory. Dependencies are
deliberately excluded — pacman/yay resolve those automatically from what's
listed here.

## StarLite (Arch + Omarchy)

- `starlite-pacman.txt` — official repo packages (pacman/extra/omarchy repos)
- `starlite-aur.txt` — AUR packages (built via yay)

**Restore on a fresh install:**

```
sudo pacman -S --needed - < packages/starlite-pacman.txt
yay -S --needed - < packages/starlite-aur.txt
```

**Regenerate after installing something new:**

```
pacman -Qqen > packages/starlite-pacman.txt
pacman -Qqem > packages/starlite-aur.txt
```

(`-Qqen` = explicit + native/official; `-Qqem` = explicit + foreign/AUR)

## Other machines

infowizardair and any other Mac/Debian machines don't use pacman, so they'd
need their own manifest format (`brew bundle dump` for Homebrew, `apt-mark
showmanual` for Debian) — not set up yet.
