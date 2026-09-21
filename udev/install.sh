#!/usr/bin/env bash
# Install/update this repo's udev rules. Safe to re-run.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo cp "$script_dir/99-starlite-touchscreen.rules" /etc/udev/rules.d/99-starlite-touchscreen.rules

sudo udevadm control --reload-rules
sudo udevadm trigger --settle --subsystem-match=input

echo
echo "Done. Rules installed and reloaded."
echo
echo "IMPORTANT: if Hyprland is already running, it won't pick up the fixed"
echo "device classification until it's restarted (logout/login, or exit and"
echo "relaunch Hyprland) - libinput only classifies input devices once, at"
echo "compositor startup."
