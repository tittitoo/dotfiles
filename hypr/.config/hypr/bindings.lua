-- Keep only your personal keybinding overrides here. Add new bindings or
-- unbind defaults before replacing them.

-- See current bindings and descriptions:
--   omarchy menu keybindings --print

-- To disable every Omarchy default binding, set this in
-- ~/.config/hypr/hyprland.lua before require("default.hypr.omarchy"), then add
-- only the bindings you want below:
--   omarchy_default_bindings = false

-- To disable all preinstalled app/webapp bindings, set:
--   omarchy_preinstalled_bindings = false

-- Add a new binding.
-- o.bind("SUPER + SHIFT + R", "SSH", "alacritty -e ssh your-server")

-- Change an existing binding by unbinding it first, then binding the key again.
-- This example changes SUPER+SPACE from the launcher to the Omarchy root menu.
-- hl.unbind("SUPER + SPACE")
-- o.bind("SUPER + SPACE", "Omarchy menu", "omarchy-menu toggle root")

-- Disable a default binding without replacing it.
-- hl.unbind("SUPER + SHIFT + B")

-- Ctrl+number switches workspaces instead of Super+number (to match macOS
-- Mission Control, and to free up Super+number for in-app tab switching in
-- Ghostty/Chrome). Was: SUPER + 1..0 -> "Switch to workspace N".
for workspace = 1, 10 do
  local key = "code:" .. tostring(workspace + 9)
  hl.unbind("SUPER + " .. key)
  o.bind("CTRL + " .. key, "Switch to workspace " .. workspace, hl.dsp.focus({ workspace = tostring(workspace) }))
end

-- Manual display tint (color temperature) control via hyprsunset, driven by
-- the ADJ layer O/P keys on the toucan keyboard. The keys are labeled F13/F14
-- in the ZMK keymap and send that HID usage, but this system's default
-- keymap (pc105+inet model) resolves keycodes 191/192 to XF86Tools/
-- XF86Launch5 instead of F13/F14 - bind on what actually fires.
o.bind("XF86Tools", "Display tint warmer", "~/.config/hypr/scripts/hyprsunset-step.sh warmer")
o.bind("XF86Launch5", "Display tint cooler", "~/.config/hypr/scripts/hyprsunset-step.sh cooler")

-- Power button short-press: lock immediately instead of opening the power
-- menu (default binding). HandlePowerKey=ignore in logind lets this reach
-- Hyprland at all instead of systemd-logind handling it first.
hl.unbind("XF86PowerOff")
o.bind("XF86PowerOff", "Lock screen", "omarchy-system-lock", { locked = true })

-- Logitech MX Keys examples:
-- o.bind("SUPER + SHIFT + S", nil, "omarchy-capture-screenshot")
-- o.bind("SUPER + H", nil, "voxtype record toggle")
-- o.bind("SUPER + PERIOD", nil, "omarchy-shell shell toggle omarchy.emojis")
