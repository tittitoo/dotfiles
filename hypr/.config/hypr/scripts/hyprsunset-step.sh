#!/bin/bash
# Step hyprsunset's color temperature up/down from its live value (queried
# via `hyprctl hyprsunset temperature` with no argument), not a local cache -
# `omarchy toggle nightlight` changes the same hyprsunset temperature, and a
# cached baseline would go stale and jump unexpectedly the next time this
# script ran after a nightlight toggle.
set -euo pipefail

MIN_TEMP=3000
MAX_TEMP=6500
STEP=500

direction="${1:?usage: hyprsunset-step.sh [warmer|cooler]}"

current="$(hyprctl hyprsunset temperature 2>/dev/null)"
[[ $current =~ ^[0-9]+$ ]] || current="$MAX_TEMP"

if [ "$direction" = "warmer" ]; then
  new=$(( current - STEP ))
  [ "$new" -lt "$MIN_TEMP" ] && new="$MIN_TEMP"
else
  new=$(( current + STEP ))
  [ "$new" -gt "$MAX_TEMP" ] && new="$MAX_TEMP"
fi

hyprctl hyprsunset temperature "$new" >/dev/null

notify-send -t 1200 -h string:x-canonical-private-synchronous:hyprsunset "Display tint" "${new}K" 2>/dev/null || true
