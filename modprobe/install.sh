#!/usr/bin/env bash
# Install/update this repo's modprobe config. Safe to re-run.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo cp "$script_dir/btusb-no-autosuspend.conf" /etc/modprobe.d/btusb-no-autosuspend.conf
sudo cp "$script_dir/rtsx-usb-cardreader-blacklist.conf" /etc/modprobe.d/rtsx-usb-cardreader-blacklist.conf

# enable_autosuspend is a writable module parameter, so apply it live too -
# no reboot or module reload needed for it to take effect immediately.
echo N | sudo tee /sys/module/btusb/parameters/enable_autosuspend >/dev/null

echo
echo "Done. /etc/modprobe.d/btusb-no-autosuspend.conf installed (applies on"
echo "next module load / boot), and applied live to the running btusb module."
echo "/etc/modprobe.d/rtsx-usb-cardreader-blacklist.conf installed (applies on"
echo "next boot; not unloaded live, as rmmod can hang behind a wedged rescan)."
echo
echo "Verify: cat /sys/module/btusb/parameters/enable_autosuspend  (should print N)"
echo "        lsmod | grep rtsx_usb_   (after reboot: no sdmmc/ms lines)"
