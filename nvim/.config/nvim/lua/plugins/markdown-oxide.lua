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
    -- A plain-table opts would be evaluated the moment lazy.nvim first
    -- reads this file to discover the plugin spec -- at Neovim startup,
    -- before nvim-lspconfig's own lsp/*.lua files are registered with
    -- vim.lsp.config, and before blink.cmp is necessarily requireable.
    -- Deferring both to a function makes them run once nvim-lspconfig
    -- itself actually loads, when both are guaranteed available.
    opts = function(_, opts)
      opts.servers = opts.servers or {}
      opts.servers.marksman = false
      opts.servers.markdown_oxide = {
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
      }
      -- nvim-lspconfig's own default filetypes for tailwindcss include
      -- "markdown"/"mdx"/"astro-markdown" (for raw HTML+Tailwind embedded
      -- in markdown), but that's not this vault's use case -- it just
      -- means tailwindcss silently attaches to every note alongside
      -- markdown_oxide and zotero_ls, competing for the same buffer for
      -- no benefit. Drop the markdown-flavored entries; keep everything
      -- else nvim-lspconfig ships (html/css/js/vue/etc.) untouched.
      opts.servers.tailwindcss = {
        filetypes = vim.tbl_filter(function(ft)
          return not vim.tbl_contains({ "markdown", "mdx", "astro-markdown" }, ft)
        end, vim.lsp.config.tailwindcss.filetypes),
      }
      return opts
    end,
  },
}
