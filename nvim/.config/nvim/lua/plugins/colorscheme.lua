return {
  -- Configure LazyVim to load desired colorscheme
  { "catppuccin/nvim", name = "catppuccin", priority = 1000 },
  { "rebelot/kanagawa.nvim", name = "kanagawa", priority = 1000 },
  {
    "LazyVim/LazyVim",
    opts = {
      -- colorscheme = "retrobox",
      -- colorscheme = "zellner",
      -- colorscheme = "catppuccin-latte",
      -- colorscheme = "catppuccin-mocha",
      -- colorscheme = "catppuccin-macchiato",
      -- colorscheme = "catppuccin-frappe",
      -- colorscheme = "kanagawa-wave",
      colorscheme = "kanagawa-dragon",
      -- colorscheme = "kanagawa-lotus",
    },
  },
}
