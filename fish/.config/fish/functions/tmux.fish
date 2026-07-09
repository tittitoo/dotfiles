# Override `tmux` with no args: attach/create "main" instead of a
# bare numbered session. Mirrors the auto-attach logic in config.fish.
function tmux --wraps=tmux
    if test (count $argv) -eq 0
        command tmux attach -t main; or command tmux new -s main
    else
        command tmux $argv
    end
end
