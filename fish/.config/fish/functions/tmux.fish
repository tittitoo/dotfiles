# Override `tmux` with no args: attach/create ai_general instead of a
# bare numbered session. Mirrors the auto-attach logic in config.fish.
function tmux --wraps=tmux
    if test (count $argv) -eq 0
        if command tmux has-session -t ai_general 2>/dev/null
            command tmux attach-session -t ai_general
        else
            tmuxinator start ai_general
        end
    else
        command tmux $argv
    end
end
