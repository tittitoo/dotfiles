-- Enables markdown-oxide (PKM language server: wikilinks, tags, backlinks,
-- daily notes) in place of marksman, which lang.markdown registers by
-- default -- markdown_oxide is a superset of what marksman offers here,
-- and running both attached to the same buffer just duplicates
-- completions/diagnostics.
return {
  {
    "mason-org/mason.nvim",
    opts = { ensure_installed = { "markdown-oxide" } },
  },
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        marksman = false,
        markdown_oxide = {
          -- blink.cmp's completion capabilities (resolveSupport,
          -- labelDetailsSupport, etc.) aren't applied to LSP servers
          -- globally by LazyVim -- only the java extra opts into them. The
          -- author's own reference config (github.com/Feel-ix-343/
          -- Neovim-Config) builds markdown_oxide's capabilities from
          -- nvim-cmp's equivalent full-capabilities helper, not bare
          -- defaults; mirror that here. Also required: dynamicRegistration
          -- for didChangeWatchedFiles, so markdown-oxide can track file
          -- renames/creates for its reference/backlink tracking.
          capabilities = vim.tbl_deep_extend("force", require("blink.cmp").get_lsp_capabilities(), {
            workspace = {
              didChangeWatchedFiles = {
                dynamicRegistration = true,
              },
            },
          }),
        },
      },
    },
  },
}
