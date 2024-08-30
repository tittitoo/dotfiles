# .zshrc config file
# 
# https://stackoverflow.com/questions/2499794/how-to-fix-a-locale-setting-warning-from-perlOO
# Setting for the new UTF-8 terminal support
export LANG="en_US.UTF-8"
LC_CTYPE=en_US.UTF-8
LC_ALL=en_US.UTF-8
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Environment Variables ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set to superior editing mode, i.e. vim
set -o vi 

export VISUAL=nvim
export EDITOR=nvim
export TERM="tmux-256color"

# Directories

export REPOS="$HOME/Repos"
export GITUSER="tittitoo"
export GHREPOS="$REPOS/github.com/$GITUSER"
export DOTFILES="$GHREPOS/dotfiles"
export SCRIPTS="$HOME/.config/scripts"  # Configured this way so that scripts folder is also symlinked to dotfiles/scripts

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Path configuration ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# File globbing
# [Bash to Zsh: File Globbing and ‘no matches found’ Errors : Bart Busschots](https://tinyurl.com/2ahdqngr)
# If wild card is not found in bash it produces warning and execute. zsh throws error and stop.
# below option mimic bash behaviour
setopt null_glob

# [setopt extended_glob](https://tinyurl.com/2463wdmk)
setopt extended_glob

# Below is based on brew doctor
export PATH="/usr/local/sbin:$PATH"

# Homebrew Setting
export HOMEBREW_NO_ENV_HINTS=TRUE

# Only run these on Debian, Ubuntu and Fedora
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  export PATH="$HOME/.local/bin:$PATH"
fi

path=(
  $path   # keep existing PATH entries
  $SCRIPTS # own scripts file above
  )

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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Prompt ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# [Pure Prompt](https://github.com/sindresorhus/pure)

PURE_GIT_PULL=0 # Prevent pure from checking whether git remote is updated


if [[ "$OSTYPE" == darwin* ]]; then
  fpath+=("$(brew --prefix)/share/zsh/site-functions")
else
  fpath+=($HOME/.zsh/pure)
  # Required by brew to set environment path on linux. 
  eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi

autoload -U promptinit; promptinit
prompt pure


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Aliases/Shortcuts ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

alias v=nvim

alias scripts='cd $SCRIPTS'
alias c='clear'
alias e='exit'
alias t='tmux'

# Repos

alias dot='cd $GHREPOS/dotfiles'

# ls

alias ls=lsd
alias la='lsd -la'

# cd
alias sb='cd ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/second_brain'

# LaunchBar Snippets folder
alias sp='cd ~/Library/Application\ Support/LaunchBar/Snippets'

# Minimalist Repo
alias mini='cd ~/Repos/github.com/tittitoo/minimalist'

# fzf aliases
# use fp to do a fzf search and preview the files
alias fp="fzf --preview 'bat --style=numbers --color=always --line-range :500 {}'"

# Source .zshrc
alias sz='source ~/.zshrc'

# search for a file with fzf and open it in vim
alias vf='v "$(fp)"'

# search for a file with fzf and open it in default system application
alias of='open "$(fp)"'

# finds all files recursively and sorts by last modification, ignore hidden files
alias lastmod='find . -type f -not -path "*/\.*" -exec ls -lrt {} +'

# Git

alias gp='git pull'
alias gs='git status'
alias lg='lazygit'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Sourcing ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

source "$HOME/.privaterc" # coming soon
source <(fzf --zsh)

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

# zoxide configuration at the end of the file
eval "$(zoxide init zsh)"
