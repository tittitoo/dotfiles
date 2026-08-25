# Override `tmux` with no args: attach/create "dragon" (via sesh/tmuxinator)
# instead of a bare numbered session. Mirrors the auto-attach logic in config.fish.
function tmux --wraps=tmux
    if test (count $argv) -eq 0
        sesh connect --tmuxinator dragon
    else
        command tmux $argv
    end
end
