-- I do the blink setup here as there is conflict if I enable from LazyExtra
-- Put nerog as nvim-cmp source
return {
  "saghen/blink.cmp",
  version = not vim.g.lazyvim_blink_main and "*",
  build = vim.g.lazyvim_blink_main and "cargo build --release",
  opts_extend = {
    "sources.completion.enabled_providers",
    "sources.compat",
  },
  dependencies = {
    "rafamadriz/friendly-snippets",
    -- add blink.compat to dependencies
    {
      "saghen/blink.compat",
      optional = true, -- make optional so it's only enabled if any extras need it
      opts = {},
      version = not vim.g.lazyvim_blink_main and "*",
    },
  },
  event = "InsertEnter",

  ---@module 'blink.cmp'
  ---@type blink.cmp.Config
  opts = {
    highlight = {
      -- sets the fallback highlight groups to nvim-cmp's highlight groups
      -- useful for when your theme doesn't support blink.cmp
      -- will be removed in a future release, assuming themes add support
      use_nvim_cmp_as_default = false,
    },
    -- set to 'mono' for 'Nerd Font Mono' or 'normal' for 'Nerd Font'
    -- adjusts spacing to ensure icons are aligned
    nerd_font_variant = "mono",
    completion = {
      menu = {
        winblend = vim.o.pumblend,
        draw = { treesitter = true },
      },
      documentation = {
        auto_show = true,
        auto_show_delay_ms = 200,
      },
      ghost_text = {
        enabled = vim.g.ai_cmp,
      },
    },

    -- experimental auto-brackets support
    accept = { auto_brackets = { enabled = true } },

    -- experimental signature help support
    -- trigger = { signature_help = { enabled = true } }
    sources = {
      -- adding any nvim-cmp sources here will enable them
      -- with blink.compat
      "neorg",
      compat = {},
      completion = {
        -- remember to enable your providers here
        enabled_providers = { "lsp", "path", "snippets", "buffer" },
      },
    },

    keymap = {
      preset = "enter",
      ["<Tab>"] = {
        LazyVim.cmp.map({ "snippet_forward", "ai_accept" }),
        "fallback",
      },
    },
  },
  ---@param opts blink.cmp.Config | { sources: { compat: string[] } }
  config = function(_, opts)
    -- setup compat sources
    local enabled = opts.sources.completion.enabled_providers
    for _, source in ipairs(opts.sources.compat or {}) do
      opts.sources.providers[source] = vim.tbl_deep_extend(
        "force",
        { name = source, module = "blink.compat.source" },
        opts.sources.providers[source] or {}
      )
      if type(enabled) == "table" and not vim.tbl_contains(enabled, source) then
        table.insert(enabled, source)
      end
    end
    require("blink.cmp").setup(opts)
  end,
}
