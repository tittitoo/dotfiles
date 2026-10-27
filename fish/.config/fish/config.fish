# fish config

# Locale. fish (unlike bash's login profile here) never set LANG, leaving it
# unset -> "C" locale. tmux specifically checks the locale of whatever shell
# invokes `tmux attach` to decide client_utf8; with no LANG, tmux concludes
# the client can't handle UTF-8 and mangles/strips multi-byte characters
# (Nerd Font icons, etc.) for every session attached from this shell.
set -gx LANG en_SG.UTF-8

# Default editor. Left unset, many tools (crontab -e, less, fzf bindings,
# etc.) fall back to the system vi/vim rather than nvim.
set -gx EDITOR nvim
set -gx VISUAL nvim

# PATH — fish_add_path -P: prepends directly to PATH (not universal fish_user_paths),
# skips silently if already present. Last call wins highest priority.
fish_add_path -P $HOME/.local/bin
fish_add_path -P $HOME/.cargo/bin
fish_add_path -P $HOME/Repos/github.com/tittitoo/mee
fish_add_path -P $HOME/Repos/github.com/tittitoo/minimalist
fish_add_path -P $HOME/Repos/github.com/tittitoo/docr

# Ruby gem user install bin dir (e.g. tmuxinator installed via `gem install --user-install`)
if type -q ruby
    fish_add_path -P (ruby -e 'print Gem.user_dir')/bin
end

# Homebrew
if test (uname -s) = Darwin
    if test (uname -m) = arm64
        set -gx HOMEBREW_PREFIX /opt/homebrew
    else
        set -gx HOMEBREW_PREFIX /usr/local
    end
else
    set -gx HOMEBREW_PREFIX /home/linuxbrew/.linuxbrew
end

# WeasyPrint / image.nvim library paths (macOS only)
# Intel: /usr/local/lib (already in default search path, but explicit doesn't hurt)
# Apple Silicon: /opt/homebrew/lib (not in default search path, so required)
if test (uname -s) = Darwin
    set -gx DYLD_LIBRARY_PATH $HOMEBREW_PREFIX/lib $DYLD_LIBRARY_PATH
end
fish_add_path -P $HOMEBREW_PREFIX/bin
fish_add_path -P $HOMEBREW_PREFIX/opt/coreutils/libexec/gnubin
fish_add_path -P $HOMEBREW_PREFIX/opt/ruby/bin

# image.nvim (covered by DYLD_LIBRARY_PATH above)
set -gx DYLD_FALLBACK_LIBRARY_PATH $HOMEBREW_PREFIX/lib

# Supress greeting message
set fish_greeting

# Disable fish's built-in history (atuin handles all history)
set -g fish_history ""

# Enable vi mode
fish_vi_key_bindings

# fzf
fzf --fish | source
set -x FZF_DEFAULT_COMMAND 'fd -t d --follow --exclude .git --color=never'

# Function to set FZF colors based on system appearance (macOS or Linux)
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
  --header "CTRL-O | CTRL-R | CTRL-U | CTRL-Y | CTRL-S"
  --bind "ctrl-d:change-prompt(Directories> )+reload(fd -t d --color=never)"
  --bind "ctrl-f:change-prompt(Files> )+reload(fd -t f --color=never)"
  --bind "ctrl-o:execute-silent(open {})"
  --bind "ctrl-y:execute-silent(copy-file-to-clipboard {})"
  # --bind "alt-y:execute-silent(cp -r {} ~/Downloads/)"
  --bind "ctrl-u:execute-silent(echo {} | clean-text.py | pbcopy)"
  --bind "ctrl-r:execute-silent(echo {} | clean-text-outlook.py | pbcopy)"
  --bind "ctrl-s:execute-silent(get_sharepoint_link.py {})"
  --bind "ctrl-/:change-preview-window(down|hidden)"'

    # Catppuccin Latte (light)
    set -l fzf_latte_colors '
  --color=bg+:#CCD0DA,bg:#EFF1F5,spinner:#DC8A78,hl:#D20F39
  --color=fg:#4C4F69,header:#D20F39,info:#8839EF,pointer:#DC8A78
  --color=marker:#7287FD,fg+:#4C4F69,prompt:#8839EF,hl+:#D20F39
  --color=selected-bg:#BCC0CC
  --color=border:#9CA0B0,label:#4C4F69'

    # Catppuccin Mocha (dark)
    set -l fzf_mocha_colors '
  --color=bg+:#313244,bg:#1E1E2E,spinner:#F5E0DC,hl:#F38BA8
  --color=fg:#CDD6F4,header:#F38BA8,info:#CBA6F7,pointer:#F5E0DC
  --color=marker:#B4BEFE,fg+:#CDD6F4,prompt:#CBA6F7,hl+:#F38BA8
  --color=selected-bg:#45475A
  --color=border:#6C7086,label:#CDD6F4'

    if is_dark_mode
        set -gx FZF_DEFAULT_OPTS "$fzf_base_opts $fzf_mocha_colors"
    else
        set -gx FZF_DEFAULT_OPTS "$fzf_base_opts $fzf_latte_colors"
    end
end

# Detect appearance. macOS: AppleInterfaceStyle is only set when dark mode is
# enabled. Linux: query the freedesktop appearance portal via gsettings (Omarchy
# keeps this in sync with the active theme). Hosts with neither (e.g. the Debian
# VPS, which has no desktop portal) fall back to dark.
function is_dark_mode
    if test (uname -s) = Darwin
        defaults read -g AppleInterfaceStyle &>/dev/null
        return $status
    else if command -q gsettings
        string match -q '*dark*' -- (gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null)
        return $status
    else
        return 0
    end
end

# Set FZF theme on shell startup
set_fzf_theme

# Re-pick the flavour on every launch, so a shell opened before a light/dark
# switch doesn't keep the old colours. fzf.fish and `fzf --fish` both call
# plain `fzf`, so this covers their bindings too.
function fzf --wraps fzf --description 'fzf with current light/dark colours'
    set_fzf_theme
    command fzf $argv
end

set -x FZF_CTRL_T_OPTS '--walker-skip .git,node_modules,target,.obsidian'
set -x FZF_ALT_C_OPTS '
  --walker-skip .git,node_modules,target
  --preview "tree -C {}"
  --preview-window=bottom:50%:wrap
  --bind "ctrl-u:preview-page-up,ctrl-d:preview-page-down"
  --bind "ctrl-o:execute-silent(open {})"'

# Configure keybindings for fzf
# \e means ALT, \c means CTRL
set fzf_fd_opts --color=never
set fzf_directory_opts --prompt="Directories> "
fzf_configure_bindings --directory=\cf --variables=\e\cv --history=\ca --git_status=\cg --git_log= --processes=\cp #--gi_log=\cl

# Yazi
function y
    # yazi shells out to fzf internally for its directory-jump popup; that
    # subprocess only inherits whatever $FZF_DEFAULT_OPTS was last exported,
    # so refresh it here too (the `fzf` wrapper below only catches direct
    # `fzf` invocations, not ones yazi makes on our behalf).
    set_fzf_theme
    set tmp (mktemp -t "yazi-cwd.XXXXXX")
    set err (mktemp -t "yazi-err.XXXXXX")
    yazi $argv --cwd-file="$tmp" 2> "$err"
    if set cwd (command cat -- "$tmp"); and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
        builtin cd -- "$cwd"
    end
    rm -f -- "$tmp"
    # macOS prints a harmless "MallocStackLogging: can't turn ..." line on
    # every exit; filter just that out so real stderr still surfaces.
    grep -v "MallocStackLogging" -- "$err" >&2
    rm -f -- "$err"
end

# btop.conf is gitignored -- btop rewrites color_theme (among other state) to
# whatever it last had on every exit, so a theme committed to git never
# sticks. Pick catppuccin light/dark here instead, before each launch.
function btop --wraps btop --description 'btop with current light/dark theme'
    set -l conf ~/.config/btop/btop.conf
    if test -f "$conf"
        set -l theme catppuccin_mocha
        is_dark_mode; or set theme catppuccin_latte
        set -l tmp (mktemp -t "btop-conf.XXXXXX")
        string replace -r '^color_theme = .*' "color_theme = \"$theme\"" < "$conf" > "$tmp"
        and mv "$tmp" "$conf"
    end
    command btop $argv
end

# `bid` is also a fish abbreviation (see aliases.fish) for bid.py, but
# abbreviations only expand on a live keypress (space/enter) while you're
# typing. Atuin recalling a past command drops the whole line in at once,
# so a recalled "bid ..." never gets the expand trigger and "bid" resolves
# as a plain command instead -- hence this function, so it works either way.
function bid
    bid.py $argv
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
if status --is-interactive; and command -q rbenv
    rbenv init - --no-rehash fish | source
end

# Added by Windsurf
fish_add_path -P /Users/infowizard/.codeium/windsurf/bin

set -gx XDG_CONFIG_HOME ~/.config
set -gx VOLTA_HOME "$HOME/.volta"
fish_add_path -P "$VOLTA_HOME/bin"

# pnpm
set -gx PNPM_HOME /Users/infowizard/Library/pnpm
fish_add_path -P "$PNPM_HOME"
# pnpm end

# Local secrets (gitignored, not stowed/tracked) — API keys etc.
if test -f $__fish_config_dir/secrets.fish
    source $__fish_config_dir/secrets.fish
end

# .config/scripts last = highest PATH priority (shadows system tools)
fish_add_path -P $HOME/.config/scripts

# Deduplicate PATH: keep first (highest-priority) occurrence; drop malformed
# relative entries (e.g. "Fusion.app/..." caused by old space-splitting bug)
set -gx PATH (printf '%s\n' $PATH | awk '!seen[$0]++ && /^\//')

# Auto-attach to or start "ai_dragon" tmux session (via sesh/tmuxinator)
# Skip when Atuin Desktop opens a terminal (ATUIN_TMUX_POPUP is set in that context)
# or in the Hyprland drop-down terminal (DROPTERM, see hypr/bindings.lua)
if status is-interactive; and not set -q ATUIN_TMUX_POPUP; and not set -q DROPTERM
    if not set -q TMUX
        sesh connect --tmuxinator ai_dragon
    end
end
