return {
  "jalvesaq/zotcite",
  dependencies = {
    "nvim-treesitter/nvim-treesitter",
    -- Required for :Zseek, <C-x><C-b>, and the annotation/note pickers —
    -- without it those fail with "module 'telescope.pickers' not found".
    "nvim-telescope/telescope.nvim",
  },
  -- Zotcite is a filetype plugin and loads itself for supported filetypes,
  -- but its own default list uses "latex" (not vimtex's "tex"), so "tex" is
  -- added explicitly to activate it in .tex buffers.
  config = function()
    local filetypes = { "markdown", "latex", "tex", "quarto", "rmd", "rnoweb", "pandoc", "vimwiki" }
    require("zotcite").setup({
      zotero_sqlite_path = vim.fn.expand("~/Zotero/zotero.sqlite"),
      filetypes = filetypes,
    })

    -- Zotcite's default insert-mode citation-insert map is <C-X><C-B>, but
    -- tmux's default prefix is Ctrl-b (unchanged in this config — see
    -- tmux.conf), which swallows the <C-B> half before it ever reaches
    -- Neovim, so the map silently does nothing under tmux. Rebind to <C-g>,
    -- which is free in tmux, in blink.cmp's default keymap preset, and in
    -- this config's other insert-mode maps.
    vim.api.nvim_create_autocmd("FileType", {
      pattern = filetypes,
      callback = function(args)
        vim.keymap.set("i", "<C-g>", "<Cmd>lua require('zotcite.get').citation()<CR>", {
          buffer = args.buf,
          silent = true,
          desc = "Zotcite: insert citation",
        })
      end,
    })
  end,
}
