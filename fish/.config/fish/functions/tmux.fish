# Override `tmux` with no args: attach/create "ai_dragon" (via sesh/tmuxinator)
# instead of a bare numbered session. Mirrors the auto-attach logic in config.fish.
function tmux --wraps=tmux
    if test (count $argv) -eq 0
        sesh connect --tmuxinator ai_dragon
    else
        command tmux $argv
    end
end
