-- Change the default Omarchy look'n'feel.

-- https://wiki.hypr.land/Configuring/Basics/Variables/#general
hl.config({
  general = {
    border_size = 1,
  },
})

-- https://wiki.hypr.land/Configuring/Basics/Variables/#decoration
hl.config({
  decoration = {
    -- Use round window corners.
    rounding = 8,
  },
})

-- https://wiki.hypr.land/Configuring/Basics/Variables/#animations
-- hl.config({
--   animations = {
--     -- Disable all animations.
--     enabled = false,
--   },
-- })

-- https://wiki.hypr.land/Configuring/Basics/Variables/#layout
-- hl.config({
--   layout = {
--     -- Avoid overly wide single-window layouts on wide screens.
--     single_window_aspect_ratio = { 1, 1 },
--   },
-- })

-- https://wiki.hypr.land/Configuring/Layouts/Scrolling-Layout/
-- hl.config({
--   scrolling = {
--     -- See only one column per screen instead of two.
--     column_width = 0.97,
--   },
-- })

-- Show Me The Key: float the keystroke overlay like KeyCastr instead of
-- tiling it as a normal window. Matches on title too since the main app
-- window shares the same class.
-- Show Me The Key: float the keystroke overlay like KeyCastr instead of
-- tiling it as a normal window. Matches on class only (not title -- Hyprland
-- doesn't reliably match titles GTK apps set after window creation); safe
-- since the main app window (same class) is only ever launched with -A
-- (--no-app-win), so it never coexists with the overlay.
o.window("one.alynx.showmethekey", {
  tag = "-default-opacity",
  float = true,
  pin = true,
  no_initial_focus = true,
  border_size = 0,
  opacity = "1 1",
  size = { 600, 150 },
  -- Hardcoded for the 2160x1440 eDP-1 panel; the monitor_w/monitor_h
  -- expression syntax (used successfully elsewhere, e.g. webcam-overlay.lua)
  -- wasn't resolving correctly for this window, so bottom-center is computed
  -- directly instead.
  move = { 780, 1230 },
})
