return {
  {
    "rebelot/kanagawa.nvim",
    name = "kanagawa",
    priority = 1000,
    opts = {
      transparent = true,
      theme = "lotus",
    },
    -- This function is executed after the plugin and its options are set.
    -- We now only pass the `opts` variable, since that's all we use.
    config = function(opts)
      require("kanagawa").setup(opts)
      -- vim.cmd.colorscheme("kanagawa") -- change theme here for wave, dragon and lotus
      -- vim.cmd.colorscheme("kanagawa-dragon") -- change theme here for wave, dragon and lotus
      -- vim.cmd.colorscheme("kanagawa-wave") -- change theme here for wave, dragon and lotus
      -- vim.cmd([[colorscheme kanagawa]])

      -- Overriding the background for UI elements to be transparent
      vim.cmd([[
      hi Normal       guibg=NONE ctermbg=NONE
      hi NormalFloat  guibg=NONE ctermbg=NONE
      hi StatusLine   guibg=NONE ctermbg=NONE
      hi StatusLineNC guibg=NONE ctermbg=NONE
      hi WinBar       guibg=NONE ctermbg=NONE
      hi WinBarNC     guibg=NONE ctermbg=NONE
      hi TabLine      guibg=NONE ctermbg=NONE
      hi TabLineFill  guibg=NONE ctermbg=NONE
      hi Folded       guibg=NONE ctermbg=NONE
    ]])
    end,
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "kanagawa-wave",
    },
  },
}
