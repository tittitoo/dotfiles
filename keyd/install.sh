#!/usr/bin/env bash
# Install/update the keyd config for this repo's home-row-mod USB keyboard setup.
# Safe to re-run. Does NOT touch [ids] in usb-keyboard.conf — see README.md;
# that value is specific to one physical USB port on one machine and must be
# re-derived per machine (or per port) by hand.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v keyd &>/dev/null; then
  echo "Installing keyd..."
  sudo pacman -S --needed keyd
fi

sudo cp "$script_dir/usb-keyboard.conf" /etc/keyd/usb-keyboard.conf

sudo systemctl enable --now keyd
sudo keyd reload

echo
echo "Done. Config installed and keyd (re)loaded."
echo
echo "IMPORTANT: the [ids] line in usb-keyboard.conf is tied to a specific"
echo "physical USB port on the machine it was generated on. If this is a new"
echo "machine, or the keyboard is in a different port, follow README.md to"
echo "look up the correct id and edit usb-keyboard.conf before trusting the"
echo "remap to be active for the right device."
