# .zshrc config file

# https://stackoverflow.com/questions/2499794/how-to-fix-a-locale-setting-warning-from-perlOO
# Setting for the new UTF-8 terminal support
export LANG="en_US.UTF-8"
LC_CTYPE=en_US.UTF-8
LC_ALL=en_US.UTF-8
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Environment Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set to superior editing mode, i.e. vim
set -o vi 

# export TERM="tmux-256color" #
# Directories

# File globbing
# [Bash to Zsh: File Globbing and ‘no matches found’ Errors : Bart Busschots](https://tinyurl.com/2ahdqngr)
# If wild card is not found in bash it produces warning and execute. zsh throws error and stop.
# below option mimic bash behaviour
setopt null_glob #

# [setopt extended_glob](https://tinyurl.com/2463wdmk)
setopt extended_glob #

# Below is based on brew doctor
# export PATH="/usr/local/sbin:$PATH"

# Only run these on Debian, Ubuntu and Fedora
# If there's brew, add linuxbrew path
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  export PATH="$HOME/.local/bin:/home/linuxbrew/.linuxbrew/bin:$PATH"
fi

# Ruby setting based on Homebrew input
export PATH="$(brew --prefix)/opt/ruby/bin:$PATH"

# To manage ruby environment, goes with rbenv instead as follows.
eval "$(rbenv init - zsh)"

path=( $path )   # keep existing PATH entries

# Remove duplicate entries and non-existent Directories
typeset -U path
path=($^path(N-/))

export PATH

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ History ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HISTFILE=~/.zsh_history
HISTSIZE=50000
SAVEHIST=50000

setopt HIST_IGNORE_SPACE  # Don't save when prefixed with space
setopt HIST_IGNORE_DUPS # Don't save duplicate lines
setopt HIST_IGNORE_ALL_DUPS # Don't save all duplicate lines regardless of event
setopt SHARE_HISTORY  # Share history between sessions

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ fzf ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# fzf options
# Use the following if we want to follow symbolic links and also including hidden files.
export FZF_DEFAULT_COMMAND='fd --follow --exclude .git'
export FZF_DEFAULT_OPTS='
  --height=60%
  --tmux=70%
  --layout=reverse
  --info=inline
  --preview="echo {}"
  --preview-window=down:3:wrap
  --color=bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc,hl:#f38ba8
  --color=fg:#cdd6f4,header:#f38ba8,info:#cba6f7,pointer:#f5e0dc
  --color=marker:#b4befe,fg+:#cdd6f4,prompt:#cba6f7,hl+:#f38ba8
  --color=selected-bg:#45475a
  --border 
  --multi
  --bind "ctrl-u:preview-page-up,ctrl-d:preview-page-down"
  --header "CTRL-T: Directories / CTRL-F: Files / CTRL-O: Open File / CTRL-Y: Download"
  --bind "ctrl-t:change-prompt(Directories> )+reload(fd -t d)"
  --bind "ctrl-f:change-prompt(Files> )+reload(fd -t f)"
  --bind "ctrl-o:execute(open {})" 
  --bind "ctrl-y:execute(cp {} ~/Downloads/)"
  --bind "ctrl-/:change-preview-window(down|hidden|)"'
# Preview file content using bat (https://github.com/sharkdp/bat)
# CRTL-T looks for files and upon enter, output the file path into console
export FZF_CTRL_T_OPTS='
  --walker-skip .git,node_modules,target,.obsidian'
# CTRL-Y to copy the command into clipboard using pbcopy
# CTRL-R looks for command history and upon enter, output the file path into console
# CTRL-R will be overriden by atuin as atuin runs last.
export FZF_CTRL_R_OPTS="
  --bind 'ctrl-y:execute-silent(echo -n {2..} | pbcopy)+abort'
  --color header:italic
  --header 'Press CTRL-Y to copy command into clipboard'"
# Print tree structure in the preview window
# ALT-C looks for directories and upon enter cd into the selected directory.
export FZF_ALT_C_OPTS='
  --walker-skip .git,node_modules,target
  --preview "tree -C {}"
  --preview-window=bottom:50%:wrap
  --bind "ctrl-u:preview-page-up,ctrl-d:preview-page-down"
  --bind "ctrl-o:execute(open {})"'

# search hook bookmarks and open them in system application
# need hookmark to be installed and hoop app
# limit the path so it shows head and tail, otherwise, some paths are too long
# alias h='hook list | fzf --delimiter="/" --with-nth=1,-2.. --print0 | xargs -0 -I {} open "{}"'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ yazi ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# [Quick Start | Yazi](https://yazi-rs.github.io/docs/quick-start)

function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
	yazi "$@" --cwd-file="$tmp"
	if cwd="$(command cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
		builtin cd -- "$cwd"
	fi
	rm -f -- "$tmp"
}
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Sourcing ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

source "$HOME/.privaterc" # coming soon
source <(fzf --zsh)
# zsh-autosuggestions
source $(brew --prefix)/share/zsh-autosuggestions/zsh-autosuggestions.zsh
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Conda ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/Users/infowizard/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/Users/infowizard/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/Users/infowizard/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/Users/infowizard/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Tools ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Install tools
eval "$(thefuck --alias)"
eval "$(atuin init zsh)"
eval "$(starship init zsh)"

# zoxide configuration at the end of the file
eval "$(zoxide init zsh)"
