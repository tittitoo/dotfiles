#!/usr/bin/env bash
# Install/update this repo's systemd-logind overrides. Safe to re-run.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo mkdir -p /etc/systemd/logind.conf.d
sudo cp "$script_dir/10-ignore-power-button.conf" /etc/systemd/logind.conf.d/10-ignore-power-button.conf

sudo systemctl restart systemd-logind

echo
echo "Done. Config installed and systemd-logind restarted (your session is"
echo "unaffected)."
