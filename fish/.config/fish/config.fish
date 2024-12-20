# fish config

# PATH
set -gx PATH /usr/local/opt/coreutils/libexec/gnubin $PATH
set -gx PATH $HOME/.local/bin $PATH
set -gx PATH $HOME/.cargo/bin $PATH
set -gx PATH $HOME/.config/scripts $PATH

# Homebrew PATH setting

if test (uname -s) = Darwin
    if test (uname -m) = arm64
        set -gx HOMEBREW_PREFIX /opt/homebrew
    else
        set -gx HOMEBREW_PREFIX /usr/local
    end
else
    set -gx HOMEBREW_PREFIX /home/linuxbrew/.linuxbrew
end

set -gx PATH $HOMEBREW_PREFIX/bin $PATH

# ruby PATH
set -gx PATH $HOMEBREW_PREFIX/opt/ruby/bin $PATH

# python PATH
set -gx PATH $HOMEBREW_PREFIX/bin/python3.13 $PATH

# image.nvim
set -gx DYLD_FALLBACK_LIBRARY_PATH $HOMEBREW_PREFIX/lib

# remove duplicate path entries
set -gx PATH (echo $PATH | tr ' ' '\n' | sort -u | sed 's/:$//')

# Supress greeting message
set fish_greeting

# Enable vi mode
set fish_vi_key_bindings

# fzf
# fzf source
fzf --fish | source
# set awk_cmd '{gsub(/^[0-9]*\/|\//, ""); print}'
set awk_cmd 'gsub(/^[0-9]*\/|\//, ""); print'
# --bind "ctrl-n:execute(echo {} | awk '{gsub(/^[0-9]*\/|\//, \"\"); print}' | pbcopy)"
# --bind "ctrl-n:execute(echo {} | awk \'{gsub(\/^[0-9]+\/, \"\"); print}\' | pbcopy)"
# --bind "ctrl-u:execute(echo {} | pbcopy)"
set -x FZF_DEFAULT_COMMAND 'fd --follow --exclude .git'
set -x FZF_DEFAULT_OPTS '
  --height=60%
  --layout=reverse
  --info=inline
  --preview="echo {}"
  --preview-window=down:3:wrap
  --color=fg:#dcd7ba,hl:#7e9cd8 
  --color=fg+:#c8c093,bg+:#2d4f67,hl+:#957fb8 
  --color=info:#a3d4d5,prompt:#dca561,pointer:#e46876,marker:#98bb6c,spinner:#7fb4ca
  --border 
  --multi
  --header "CTRL-D: Directories / CTRL-F: Files / CTRL-O: Open File / CTRL-Y: Download / CTRL-U: Copy Name / CTRL-/: Change Preview"
  --bind "ctrl-d:change-prompt(Directories> )+reload(fd -t d)"
  --bind "ctrl-f:change-prompt(Files> )+reload(fd -t f)"
  --bind "ctrl-o:execute(open {})" 
  --bind "ctrl-y:execute(cp {} ~/Downloads/)"
  --bind "ctrl-u:execute(echo {} | clean-text | pbcopy)"
  --bind "ctrl-/:change-preview-window(down|hidden)"'

set -x FZF_CTRL_T_OPTS '--walker-skip .git,node_modules,target,.obsidian'
set -x FZF_ALT_C_OPTS '
  --walker-skip .git,node_modules,target
  --preview "tree -C {}"
  --preview-window=bottom:50%:wrap
  --bind "ctrl-u:preview-page-up,ctrl-d:preview-page-down"
  --bind "ctrl-o:execute(open {})"'

#   --bind "ctrl-n:preview-page-up,ctrl-p:preview-page-down"

# Configure keybidings for fzf
# \e means ALT, \c means CTRL
fzf_configure_bindings --directory=\cf --variables=\e\cv --history=\ch --git_status=\cg --git_log= --processes=\cp #--gi_log=\cl


# fiz.fish
# set fzf_preview_dir_cmd eza --all --color=always

# Yazi
function y
    set tmp (mktemp -t "yazi-cwd.XXXXXX")
    yazi $argv --cwd-file="$tmp"
    if set cwd (command cat -- "$tmp"); and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
        builtin cd -- "$cwd"
    end
    rm -f -- "$tmp"
end

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
if test -f /Users/infowizard/anaconda3/bin/conda
    eval /Users/infowizard/anaconda3/bin/conda "shell.fish" hook $argv | source
end
# <<< conda initialize <<<

# Atuin
atuin init fish | source

# Starship
starship init fish | source

# zoxide
zoxide init fish | source

# Added by `rbenv init` on Tue Oct 22 13:11:31 +08 2024
status --is-interactive; and rbenv init - --no-rehash fish | source

# Added by Windsurf
fish_add_path /Users/infowizard/.codeium/windsurf/bin
