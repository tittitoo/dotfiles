# Claude Code checks npm's "latest" tag, which is usually ahead of the
# GitHub releases mise upgrades from -> a permanent "mise upgrade claude"
# nag even when already current.
set -gx DISABLE_AUTOUPDATER 1
