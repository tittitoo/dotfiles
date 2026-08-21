return {
  "jalvesaq/zotcite",
  dependencies = {
    "nvim-treesitter/nvim-treesitter",
  },
  -- Zotcite is a filetype plugin and loads itself for supported filetypes,
  -- but its own default list uses "latex" (not vimtex's "tex"), so "tex" is
  -- added explicitly to activate it in .tex buffers.
  config = function()
    require("zotcite").setup({
      zotero_sqlite_path = vim.fn.expand("~/Zotero/zotero.sqlite"),
      filetypes = { "markdown", "latex", "tex", "quarto", "rmd", "rnoweb", "pandoc", "vimwiki" },
    })
  end,
}
