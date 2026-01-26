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
set -x FZF_DEFAULT_COMMAND 'fd -t d --follow --exclude .git --color=never'

# Function to set FZF colors based on macOS appearance
function set_fzf_theme
    # Base options (non-color)
    set -l fzf_base_opts '
  --height=80%
  --layout=reverse
  --info=inline
  --prompt="Directories> "
  --preview="echo {}"
  --preview-window=down:3:wrap:hidden
  --border=rounded
  --multi
  --header "CTRL-D / CTRL-F / CTRL-O / CTRL-Y / CTRL-U / CTRL-R / CTRL-S / CTRL-/"
  --bind "ctrl-d:change-prompt(Directories> )+reload(fd -t d --color=never)"
  --bind "ctrl-f:change-prompt(Files> )+reload(fd -t f --color=never)"
  --bind "ctrl-o:execute-silent(open {})"
  --bind "ctrl-y:execute-silent(cp -r {} ~/Downloads/)"
  --bind "ctrl-u:execute-silent(echo {} | clean-text | pbcopy)"
  --bind "ctrl-r:execute-silent(echo {} | clean-text-outlook | pbcopy)"
  --bind "ctrl-s:execute-silent(get_sharepoint_link.py {})"
  --bind "ctrl-/:change-preview-window(down|hidden)"'

    # Catppuccin Latte (light)
    set -l fzf_latte_colors '
  --color=bg+:#CCD0DA,bg:-1,spinner:#DC8A78,hl:#D20F39
  --color=fg:#4C4F69,header:#D20F39,info:#8839EF,pointer:#DC8A78
  --color=marker:#7287FD,fg+:#4C4F69,prompt:#8839EF,hl+:#D20F39
  --color=selected-bg:#BCC0CC
  --color=border:#9CA0B0,label:#4C4F69'

    # Catppuccin Mocha (dark)
    set -l fzf_mocha_colors '
  --color=bg+:#313244,bg:-1,spinner:#F5E0DC,hl:#F38BA8
  --color=fg:#CDD6F4,header:#F38BA8,info:#CBA6F7,pointer:#F5E0DC
  --color=marker:#B4BEFE,fg+:#CDD6F4,prompt:#CBA6F7,hl+:#F38BA8
  --color=selected-bg:#45475A
  --color=border:#6C7086,label:#CDD6F4'

    # Detect macOS appearance (AppleInterfaceStyle is only set when dark mode is enabled)
    if defaults read -g AppleInterfaceStyle &>/dev/null
        set -gx FZF_DEFAULT_OPTS "$fzf_base_opts $fzf_mocha_colors"
    else
        set -gx FZF_DEFAULT_OPTS "$fzf_base_opts $fzf_latte_colors"
    end
end

# Set FZF theme on shell startup
set_fzf_theme

set -x FZF_CTRL_T_OPTS '--walker-skip .git,node_modules,target,.obsidian'
set -x FZF_ALT_C_OPTS '
  --walker-skip .git,node_modules,target
  --preview "tree -C {}"
  --preview-window=bottom:50%:wrap
  --bind "ctrl-u:preview-page-up,ctrl-d:preview-page-down"
  --bind "ctrl-o:execute-silent(open {})"'

#   --bind "ctrl-n:preview-page-up,ctrl-p:preview-page-down"

# Configure keybidings for fzf
# \e means ALT, \c means CTRL
set fzf_fd_opts --color=never
set fzf_directory_opts --prompt="Directories> "
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
set -gx PNPM_HOME /Users/infowizard/Library/pnpm
if not string match -q -- $PNPM_HOME $PATH
    set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end
