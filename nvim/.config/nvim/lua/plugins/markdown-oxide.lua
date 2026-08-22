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
          -- Required by markdown-oxide to track file renames/creates for
          -- its reference/backlink tracking.
          capabilities = {
            workspace = {
              didChangeWatchedFiles = {
                dynamicRegistration = true,
              },
            },
          },
        },
      },
    },
  },
}
