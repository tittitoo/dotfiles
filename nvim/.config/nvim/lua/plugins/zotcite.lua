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

        -- za/zb/zi/zo/zv are zotcite's own defaults (all fields, abstract,
        -- quick info, open attachment, view compiled doc) -- none of them
        -- reveal the item in Zotero's own library pane, which is what a
        -- Hookmark-style "jump to this reference" shortcut needs (PDF
        -- Expert, not Zotero's built-in viewer, is the actual PDF reader
        -- here, so zo's "open attachment" isn't it). get_ref_data's
        -- zotkey field is items.key from Zotero's DB -- the standard
        -- 8-char id zotero://select/library/items/<key> expects.
        vim.keymap.set("n", "<leader>zs", function()
          local key = require("zotcite.get").citation_key()
          if key == "" then
            vim.notify("No citation under cursor", vim.log.levels.WARN, { title = "zotcite" })
            return
          end
          local repl = require("zotcite.zotero").get_ref_data(key)
          if type(repl) ~= "table" or not repl.zotkey then
            vim.notify("Citation key not found", vim.log.levels.WARN, { title = "zotcite" })
            return
          end
          vim.fn.jobstart(
            { "open", "zotero://select/library/items/" .. repl.zotkey },
            { detach = true }
          )
        end, {
          buffer = args.buf,
          silent = true,
          desc = "Zotcite: select item in Zotero",
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

          -- zotero_ls's completion handler always replies with isIncomplete =
          -- false (zotcite/lsp.lua), even for the very first request fired the
          -- instant "@" is typed — at that point there's no search text yet, so
          -- it legitimately returns 0 items. blink.cmp reads isIncomplete=false
          -- as "this answer covers everything you'll type going forward" and
          -- switches to filtering that (empty) cached list locally instead of
          -- re-querying, so zotero_ls's real matches for "@word" never surface.
          -- Force isIncomplete = true so blink re-requests zotero_ls on every
          -- keystroke, matching how it actually recomputes matches from scratch
          -- each time.
          -- zotero_ls's completion handler also always builds a textEdit range
          -- covering exactly one character (character-1 to character), no
          -- matter how long the citation search text actually is — a latent
          -- bug only exposed now that trigger-character-based, multi-keystroke
          -- completion is enabled. Accepting "Fuller-Nightingale-2017" for
          -- "@ful" left "@fu" in place and appended the citekey right after it
          -- instead of replacing the whole "@ful" span. Recompute the same
          -- "word after @" (or after "{" for tex/rnoweb) that zotcite/lsp.lua
          -- itself matches on, and correct each item's range to span the whole
          -- word, not just its last character.
          local orig_request = client.request
          client.request = function(self, method, params, handler, bufnr)
            if method == "textDocument/completion" and handler and params.position then
              local lnum, char = params.position.line, params.position.character
              local line = vim.api.nvim_buf_get_lines(0, lnum, lnum + 1, true)[1] or ""
              local byte_idx = vim.fn.byteidx(line, char)
              if byte_idx < 0 then byte_idx = #line end
              local subline = line:sub(1, byte_idx)
              local word
              if vim.bo.filetype == "rnoweb" or vim.bo.filetype == "tex" then
                word = subline:match(".*{.-(%S+)$")
              else
                word = subline:match(".*@(%S+)$")
              end
              local orig_handler = handler
              handler = function(err, result, ctx)
                if result then
                  result.isIncomplete = true
                  if word then
                    for _, item in ipairs(result.items or {}) do
                      if item.textEdit and item.textEdit.range and item.textEdit.range.start then
                        item.textEdit.range.start.character = char - #word
                      end
                    end
                  end
                end
                return orig_handler(err, result, ctx)
              end
            end
            return orig_request(self, method, params, handler, bufnr)
          end
        end
      end,
    })
  end,
}
