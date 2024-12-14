return {
  "saghen/blink.cmp",
  opts = {
    completion = {
      documentation = {
        auto_show = false,
        -- auto_show_delay_ms = 200,
      },
    },
    sources = {
      -- adding any nvim-cmp sources here will enable them
      -- with blink.compat
      compat = {},
      default = { "lsp", "path", "snippets", "buffer" },
      cmdline = {},
    },
  },
}
