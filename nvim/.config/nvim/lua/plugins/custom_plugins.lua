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
    -- Make blink.cmp toogleable. vim.b.completion is left unset (nil) so
    -- every buffer starts with completion ON by default; opts.enabled below
    -- treats anything other than `false` as enabled.
    opts = function(_, opts)
      Snacks.toggle({
        name = "Completion",
        get = function()
          return vim.b.completion ~= false
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

      -- markdown-oxide's tag completions all carry filterText like
      -- "#commercial" (leading "#" before the real prefix) and an identical
      -- sortText for every tag, so blink's fuzzy matcher doesn't give them
      -- the same "exact prefix" bonus a plain buffer word like
      -- "commercial-review" gets by starting clean at position 0 — tags lose
      -- to buffer noise instead of being "top priority" while typing "#tag".
      -- Boost any Keyword-kind item (markdown-oxide's tag kind) heavily, but
      -- only while the cursor is actually in a "#word" context, so this
      -- doesn't affect unrelated Keyword-kind completions elsewhere (e.g.
      -- Python's def/class).
      opts.sources.providers.lsp = opts.sources.providers.lsp or {}
      local orig_lsp_transform_items = opts.sources.providers.lsp.transform_items
      opts.sources.providers.lsp.transform_items = function(ctx, items)
        items = orig_lsp_transform_items and orig_lsp_transform_items(ctx, items) or items
        local before_cursor = ctx.line:sub(1, ctx.cursor[2])
        if before_cursor:match("#%S*$") then
          for _, item in ipairs(items) do
            if item.kind == vim.lsp.protocol.CompletionItemKind.Keyword then
              -- Flat +1000 alone ties whenever two tags both match (e.g.
              -- "#c" matching both "commercial" and "scratch"), and blink
              -- then falls back to markdown-oxide's own sortText, which
              -- isn't usage-based -- "scratch" (sortText 16) beat
              -- "commercial" (sortText 36) despite being used once vs. six
              -- times. Break the tie using markdown-oxide's own "N
              -- references" labelDetails, so more-used tags rank higher.
              local refs = 0
              local detail = item.labelDetails and item.labelDetails.detail
              if detail then refs = tonumber(detail:match("(%d+) reference")) or 0 end
              item.score_offset = (item.score_offset or 0) + 1000 + refs
            end
          end
        end
        return items
      end

      -- blink's default "label" component renders label..label_detail with
      -- no separator (config/completion/menu.lua), which is why
      -- markdown-oxide's "N references" labelDetails.detail runs straight
      -- into the tag name ("commercial6 references"). Reproduce the default
      -- component with a space inserted before label_detail, shifting the
      -- BlinkCmpLabelDetail highlight range to match.
      opts.completion = opts.completion or {}
      opts.completion.menu = opts.completion.menu or {}
      opts.completion.menu.draw = opts.completion.menu.draw or {}
      opts.completion.menu.draw.components = opts.completion.menu.draw.components or {}
      opts.completion.menu.draw.components.label = {
        width = { fill = true, max = 60 },
        text = function(ctx)
          return ctx.label .. (ctx.label_detail ~= "" and (" " .. ctx.label_detail) or "")
        end,
        highlight = function(ctx)
          local label = ctx.label
          local highlights = {
            { 0, #label, group = ctx.deprecated and "BlinkCmpLabelDeprecated" or "BlinkCmpLabel" },
          }
          if ctx.label_detail ~= "" then
            local start = #label + 1
            table.insert(highlights, { start, start + #ctx.label_detail, group = "BlinkCmpLabelDetail" })
          end
          if vim.list_contains(ctx.self.treesitter, ctx.source_id) and not ctx.deprecated then
            vim.list_extend(highlights, require("blink.cmp.completion.windows.render.treesitter").highlight(ctx))
          end
          for _, idx in ipairs(ctx.label_matched_indices) do
            table.insert(highlights, { idx, idx + 1, group = "BlinkCmpLabelMatch" })
          end
          return highlights
        end,
      }

      return opts
    end,
  },
  {
    "supermaven-inc/supermaven-nvim",
    opts = {
      disable_inline_completion = true, -- route through blink.cmp; toggled by <leader>uk
    },
    -- <leader>uk (above) turns off blink.cmp entirely. This instead stops just
    -- the Supermaven backend process, leaving LSP/buffer/path/snippets/zotcite
    -- completions on.
    config = function(_, opts)
      require("supermaven-nvim").setup(opts)

      local api = require("supermaven-nvim.api")
      -- setup() unconditionally calls api.start() with no config knob to
      -- suppress it, so stop it right back off to make "off at startup" the
      -- default; <leader>us starts it again.
      api.stop()

      Snacks.toggle({
        name = "Supermaven",
        get = api.is_running,
        set = function(state)
          if state then
            api.start()
          else
            api.stop()
          end
        end,
      }):map("<leader>us")
    end,
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
