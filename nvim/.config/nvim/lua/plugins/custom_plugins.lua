-- Custom plugins

return {
  {
    "MeanderingProgrammer/render-markdown.nvim",
    opts = {
      latex = { enabled = false },
    },
  },
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
      window = {
        backdrop = 0.8,
        width = 0.5,
        -- height = 0.8,
      },
      plugins = {
        twilight = { enabled = false },
      },
    },
  },
  -- { "folke/twilight.nvim", opts = {} },
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
    dependencies = { { "nvim-mini/mini.icons", opts = {} } },
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

      -- LazyVim's AI extra (lazyvim.plugins.extras.ai.supermaven) gives
      -- Supermaven a score_offset of 100 here so its ghost-text suggestion
      -- always wins the top completion slot — right for normal coding, but
      -- it drowns out zotcite's citation matches whenever both have a
      -- candidate (e.g. typing "@full" showed Supermaven's "actually"
      -- instead of the Fuller reference zotcite's own search correctly
      -- finds). Override only during citation search — text immediately
      -- before the cursor matching "@word", the same pattern zotcite's own
      -- matcher uses — leaving the +100 boost everywhere else untouched.
      opts.sources = opts.sources or {}
      opts.sources.providers = opts.sources.providers or {}
      opts.sources.providers.supermaven = opts.sources.providers.supermaven or {}
      opts.sources.providers.supermaven.score_offset = function(ctx)
        local before_cursor = ctx.line:sub(1, ctx.cursor[2])
        if before_cursor:match("@%S*$") then return -1000 end
        return 100
      end

      return opts
    end,
  },
  {
    "supermaven-inc/supermaven-nvim",
    opts = {
      disable_inline_completion = true, -- route through blink.cmp; toggled by <leader>uk
    },
  },

  -- Silence the bottom-right LSP progress toasts (e.g. pyright spinner/checkmark)
  {
    "folke/noice.nvim",
    opts = {
      lsp = {
        progress = { enabled = false },
      },
    },
  },

}
