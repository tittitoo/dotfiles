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
    -- Neovim, so the map silently does nothing under tmux. Ctrl-based
    -- alternatives collide with tmux, fish's fzf widgets, or blink.cmp's
    -- default keymap preset, so rebind to Alt-C (mnemonic: Citation)
    -- instead — Ghostty has macos-option-as-alt on, and no Alt/Meta map
    -- exists anywhere else in this config.
    vim.api.nvim_create_autocmd("FileType", {
      pattern = filetypes,
      callback = function(args)
        vim.keymap.set("i", "<M-c>", "<Cmd>lua require('zotcite.get').citation()<CR>", {
          buffer = args.buf,
          silent = true,
          desc = "Zotcite: insert citation",
        })
      end,
    })

    -- Zotcite runs its own fake LSP server ("zotero_ls") for completion, but
    -- deliberately leaves `@` out of its declared triggerCharacters (see
    -- zotcite/lsp.lua: "-- would work only if we could reset the
    -- completion" — a limitation the author left unresolved). blink.cmp's
    -- show_on_trigger_character (on by default) reads triggerCharacters
    -- live from client.server_capabilities on every keystroke — not a
    -- one-time snapshot — so injecting "@" here is enough to make typing
    -- "@" + letters auto-show completion, without touching the zotcite
    -- plugin's own files (which would be lost on the next update anyway).
    vim.api.nvim_create_autocmd("LspAttach", {
      callback = function(args)
        local client = vim.lsp.get_client_by_id(args.data.client_id)
        if client and client.name == "zotero_ls" then
          client.server_capabilities.completionProvider = client.server_capabilities.completionProvider
            or {}
          client.server_capabilities.completionProvider.triggerCharacters = { "@" }
        end
      end,
    })
  end,
}
