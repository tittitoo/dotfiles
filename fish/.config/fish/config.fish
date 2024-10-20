
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
if test -f /Users/infowizard/anaconda3/bin/conda
    eval /Users/infowizard/anaconda3/bin/conda "shell.fish" hook $argv | source
end
# <<< conda initialize <<<

export PATH="$PATH:$HOME/.local/bin:$HOME/.cargo/env"

# Supress greeting message
set fish_greeting

# Homebrew setting
eval "$(/opt/homebrew/bin/brew shellenv)"

# Yazi
function y
    set tmp (mktemp -t "yazi-cwd.XXXXXX")
    yazi $argv --cwd-file="$tmp"
    if set cwd (command cat -- "$tmp"); and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
        builtin cd -- "$cwd"
    end
    rm -f -- "$tmp"
end

# Atuin
atuin init fish | source

# Starship
starship init fish | source

# zoxide
zoxide init fish | source
