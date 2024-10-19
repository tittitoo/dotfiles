
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
if test -f /Users/infowizard/anaconda3/bin/conda
    eval /Users/infowizard/anaconda3/bin/conda "shell.fish" hook $argv | source
end
# <<< conda initialize <<<


export PATH="$PATH:$HOME/.local/bin"

# Atuin
atuin init fish | source

# Starship
starship init fish | source
