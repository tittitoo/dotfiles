-- Extra autostart processes.
-- o.launch_on_start("my-service")

-- Manual display tint control (bindings.lua XF86Tools/XF86Launch5) talks to
-- hyprsunset over its socket via `hyprctl hyprsunset`, so the daemon needs to
-- be running.
o.launch_on_start("hyprsunset")
