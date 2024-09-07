return {
  -- Configure LazyVim to load desired colorscheme
  { "catppuccin/nvim", name = "catppuccin", priority = 1000 },
  {
    "LazyVim/LazyVim",
    opts = {
      -- colorscheme = "retrobox",
      -- colorscheme = "zellner",
      colorscheme = "catppuccin-latte",
      -- colorscheme = "catppuccin-mocha",
      -- colorscheme = "catppuccin-macchiato",
      -- colorscheme = "catppuccin-frappe",
    },
  },
}
