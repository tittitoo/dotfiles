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
fish_vi_key_bindings
# set -g fish_key_bindings fish_vi_key_binding
# fish_key_bindings fish_mode_vi

# Load ssh id key
# eval (ssh-agent -c)
# ssh-add ~/.ssh/id_ed25519

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
  # --color=hl:#658594 
  # --color=fg:#DCD7BA,fg+:#C5C9C5,bg:-1,bg+:-1
  # --color=info:#727169,prompt:#7E9CD8,pointer:#957FB8,marker:#98BB6C,spinner:-1 
  # --color=header:#727169,border:-1,preview-fg:-1,preview-bg:-1 
  --border=rounded
  --multi
  --header "CTRL-D / CTRL-F / CTRL-O / CTRL-Y / CTRL-U / CTRL-R / CTRL-/"
  --bind "ctrl-d:change-prompt(Directories> )+reload(fd -t d)"
  --bind "ctrl-f:change-prompt(Files> )+reload(fd -t f)"
  --bind "ctrl-o:execute(open {})" 
  --bind "ctrl-y:execute(cp {} ~/Downloads/)"
  --bind "ctrl-u:execute(echo {} | clean-text | pbcopy)"
  --bind "ctrl-r:execute(echo {} | clean-text-outlook | pbcopy)"
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
fzf_configure_bindings --directory=\cf --variables=\e\cv --history=\ca --git_status=\cg --git_log= --processes=\cp #--gi_log=\cl

# Add ssh key
if test (uname -s) = Darwin
    if not test -S $SSH_AUTH_SOCK
        eval (ssh-agent -c) >/dev/null # make the output silent
        # eval (ssh-agent -c)
    end
    if test $hostname = infowizardAir
        ssh-add --apple-use-keychain -q ~/.ssh/id_ed25519
    else if test $hostname = infowizardMac
        ssh-add --apple-use-keychain -q ~/.ssh/id_ecdsa
    end
end

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

# # Start the Neovim server if not already running
# nvim_server

# Added by `rbenv init` on Tue Oct 22 13:11:31 +08 2024
status --is-interactive; and rbenv init - --no-rehash fish | source

# Added by Windsurf
fish_add_path /Users/infowizard/.codeium/windsurf/bin

set -gx XDG_CONFIG_HOME ~/.config
set -gx VOLTA_HOME "$HOME/.volta"
set -gx PATH "$VOLTA_HOME/bin" $PATH

# pnpm
set -gx PNPM_HOME "/Users/infowizard/Library/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end
