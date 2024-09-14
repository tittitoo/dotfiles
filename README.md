# My dotfile repo

The repo is kept in a place of your choosing. `stow` is then used to manage
symlinks to the correct locations. If the repo is not placed into 'Home'
folder, then `--target=$HOME` flag is required when running `stow`.

For e.g., `cd` to the directory the dotfiles are kept and run `stow
--target=$HOME nvim`.

`stow */` command will symlink all the packages defined.
