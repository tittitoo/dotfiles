return {
  {
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000,
    opts = {
      flavour = "mocha", -- auto, latte, frappe, macchiato, mocha
      -- background = { -- :h background
      --   light = "latte",
      --   dark = "mocha",
      },
      transparent_background = true,
      integrations = {
        cmp = true,
        gitsigns = true,
        treesitter = true,
        -- Disable the default nvimtree integration as it can conflict
        -- if you are using other file tree plugins
        nvimtree = false,

        -- Add the bufferline integration here.
        -- This tells Catppuccin to handle the colors for bufferline.
        bufferline = true,
      },
    },
    config = function(_, opts)
      require("catppuccin").setup(opts)

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
      -- Load bufferline *after* Catppuccin has been set up.
      -- This avoids the "attempt to call field 'get'" error.
      require("bufferline").setup({
        options = {
          offsets = {
            {
              filetype = "NvimTree",
              text = "File Explorer",
              highlight = "Directory",
              separator = true,
            },
          },
        },
      })
    end,
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "catppuccin",
    },
  },
}
