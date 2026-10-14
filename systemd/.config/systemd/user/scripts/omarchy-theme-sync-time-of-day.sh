#!/bin/bash
# Idempotently set Omarchy's theme to whichever of light/dark should be
# active right now, based on wall-clock time (light 07:00-18:59, dark
# 19:00-06:59).
#
# Replaces two independent "set to light"/"set to dark" oneshots that each
# ran on their own OnCalendar=07:00/19:00 trigger with Persistent=true. That
# design raced itself every time the machine booted or woke after missing a
# trigger: systemd fires all missed persistent timers back-to-back on
# startup, and whichever of the two oneshots happened to finish last won,
# regardless of which theme actually matched the current time. Computing the
# answer from the clock on every invocation makes repeated/simultaneous runs
# agree with each other instead of racing.
set -euo pipefail

hour=$(date +%H)
if ((10#$hour >= 7 && 10#$hour < 19)); then
  want=catppuccin-latte
else
  want=catppuccin
fi

current=$(cat "$HOME/.local/state/omarchy/current/theme.name" 2>/dev/null || true)
if [[ $current == "$want" ]]; then
  exit 0
fi

exec /usr/share/omarchy/bin/omarchy theme set "$want"
