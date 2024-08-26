export PATH="$PATH:$HOME/.local/bin"
. "$HOME/.cargo/env"

eval "$(thefuck --alias)"

# Set up fzf key bindings and fuzzy completion
eval "$(fzf --bash)"
#~~~~~~~~~~~~~~~~~~~~~~~~~ Aliases~~~~~~~~~~~~~~~~~~~~~~~~~

alias ls='ls --color=auto'
alias ll='ls -la'

# cd

alias sb='cd "/Users/infowizard/Library/Mobile Documents/iCloud~md~obsidian/Documents/second_brain"'
alias rfq='cd "/Users/infowizard/Library/CloudStorage/OneDrive-SharedLibraries-JasonElectronicsPteLtd/Bid Proposal - Documents/@rfqs"'

#~~~~~~~~~~~~~~~~~~~~~~~~~ Shortcuts~~~~~~~~~~~~~~~~~~~~~~~~~

alias v=nvim
alias t='tmux'
alias e='exit'
alias c='clear'
# fzf aliases
# use fp to do a fzf search and preview the files
alias fp="fzf --preview 'bat --style=numbers --color=always --line-range :500 {}'"
# search for a file with fzf and open it in vim
alias vf='v "$(fp)"'
# search for a file with fzf and open in default application
alias of='open "$(fp)"'
