-- Custom plugins

return {
  -- {
  --   "joshuadanpeterson/typewriter",
  --   dependencies = {
  --     "nvim-treesitter/nvim-treesitter",
  --   },
  --   config = function()
  --     require("typewriter").setup({
  --       enable_with_zen_mode = true,
  --       keep_cursor_position = true,
  --       enable_notifications = false,
  --       enable_horizontal_scroll = false,
  --     })
  --   end,
  --   opts = {},
  -- },
  {
    "folke/zen-mode.nvim",
    opts = {
      -- on_open = function()
      --   vim.cmd("TWEnable")
      -- end,
      -- on_close = function()
      --   vim.cmd("TWDisable")
      -- end,
      window = {
        width = 80,
      },
      plugins = {
        twilight = { enabled = false },
      },
    },
  },
  { "folke/twilight.nvim", opts = {} },
  {
    "jiaoshijie/undotree",
    dependencies = "nvim-lua/plenary.nvim",
    config = true,
    keys = { -- load the plugin only when using it's keybinding:
      { "<leader>u", "<cmd>lua require('undotree').toggle()<cr>" },
    },
  },

  -- oil-nvim
  {
    "stevearc/oil.nvim",
    opts = {},
    -- Optional dependencies
    dependencies = { { "echasnovski/mini.icons", opts = {} } },
    -- dependencies = { "nvim-tree/nvim-web-devicons" }, -- use if prefer nvim-web-devicons
  },
  {
    "alexghergh/nvim-tmux-navigation",
    config = function()
      local nvim_tmux_nav = require("nvim-tmux-navigation")

      nvim_tmux_nav.setup({
        disable_when_zoomed = true, -- defaults to false
      })

      vim.keymap.set("n", "<C-h>", nvim_tmux_nav.NvimTmuxNavigateLeft)
      vim.keymap.set("n", "<C-j>", nvim_tmux_nav.NvimTmuxNavigateDown)
      vim.keymap.set("n", "<C-k>", nvim_tmux_nav.NvimTmuxNavigateUp)
      vim.keymap.set("n", "<C-l>", nvim_tmux_nav.NvimTmuxNavigateRight)
      vim.keymap.set("n", "<C-\\>", nvim_tmux_nav.NvimTmuxNavigateLastActive)
      -- vim.keymap.set("n", "<C-Space>", nvim_tmux_nav.NvimTmuxNavigateNext)
    end,
  },
  -- https://github.com/3rd/image.nvim
  {
    "3rd/image.nvim",
    build = false, -- so that it doesn't build the rock https://github.com/3rd/image.nvim/issues/91#issuecomment-2453430239
    opts = {},
  },

  -- This is for blink
  {
    "saghen/blink.cmp",
    -- Make blink.cmp toogleable
    opts = function(_, opts)
      vim.b.completion = false

      Snacks.toggle({
        name = "Completion",
        get = function()
          return vim.b.completion
        end,
        set = function(state)
          vim.b.completion = state
        end,
      }):map("<leader>uk")

      opts.enabled = function()
        return vim.b.completion ~= false
      end
      return opts
    end,
  },
  -- blink.compact. This is for compatibility with blink and codeium
  -- Othereise it will output "attempt to index field 'lsp' (a nil value)" error
  -- { "saghen/blink.compat", opts = { impersonate_nvim_cmp = true } },
}
