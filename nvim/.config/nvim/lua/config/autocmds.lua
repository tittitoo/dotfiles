-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua
-- Add any additional autocmds here

-- Note-creation user commands (:Minutes, :Lit, :Dragon) for the
-- dragon vault. Loaded here since this file is already loaded on VeryLazy.
require("config.commands")

-- markdown-oxide's :Daily jump command creates the file itself (via the LSP)
-- before Neovim opens it, so it's already on disk by the time we see it --
-- that's BufReadPost, not BufNewFile. Watch both so this works regardless
-- of whether Neovim or the LSP created the file first. Only touches
-- completely empty buffers, so re-opening a day you've already written in
-- is always a no-op here.
vim.api.nvim_create_autocmd({ "BufNewFile", "BufReadPost" }, {
  pattern = "*/journal/*.md",
  callback = function(args)
    if vim.api.nvim_buf_line_count(args.buf) > 1 or vim.api.nvim_buf_get_lines(args.buf, 0, 1, false)[1] ~= "" then
      return
    end
    -- Filename is the date (dailynote = "%Y-%m-%d" in .moxide.toml). Parse
    -- it so the heading matches the note's actual day, not necessarily
    -- today -- :Daily can create entries for other days too.
    local date_str = vim.fn.fnamemodify(vim.api.nvim_buf_get_name(args.buf), ":t:r")
    local y, m, d = date_str:match("^(%d%d%d%d)-(%d%d)-(%d%d)$")
    local weekday = y
        and os.date("%A", os.time({ year = tonumber(y), month = tonumber(m), day = tonumber(d) }))
      or os.date("%A")
    vim.api.nvim_buf_set_lines(
      args.buf,
      0,
      -1,
      false,
      { "# " .. weekday .. " " .. date_str, "", "tags:", "#journal", "", "" }
    )
    vim.api.nvim_buf_call(args.buf, function()
      vim.cmd.write()
    end)
    vim.api.nvim_win_set_cursor(0, { 6, 0 })
  end,
})

-- initialize global var to false -> nvim-cmp turned off by default
-- vim.g.cmptoggle = true
--
-- require("cmp").setup({
--   enabled = function()
--     return vim.g.cmptoggle
--   end,
-- })

-- wrap and check for spell in text filetypes
-- added to disable spelling
vim.api.nvim_create_autocmd("FileType", {
  -- group = augroup("wrap_spell"),
  pattern = { "gitcommit", "markdown", "pandoc", "norg", "*.md", "tex" },
  callback = function()
    vim.opt_local.wrap = true
    vim.opt_local.spell = false
    vim.opt_local.textwidth = 75
    vim.opt_local.tabstop = 4 -- Number of spaces a <Tab> counts for
    vim.opt_local.shiftwidth = 4 -- Number of spaces used for each step of (auto)indent
    vim.opt_local.expandtab = true -- Use spaces instead of tabs
  end,
})

vim.api.nvim_create_autocmd("FileType", {
  -- group = augroup("wrap_spell"),
  pattern = { "gitcommit", "markdown", "pandoc", "norg" },
  command = "set nospell",
})

-- Auto enable wrap
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "gitcommit", "markdown", "pandoc", "norg" },
  command = "set wrap",
})

-- Disable comment from being copied
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "gitcommit", "markdown", "pandoc", "norg" },
  command = "set formatoptions-=cro", -- Disable auto-comment
})

-- Disable diagnostics by default for markdown files
-- Use <leader>ud to toggle them on (including markdownlint)
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "markdown" },
  callback = function()
    vim.diagnostic.enable(false)
  end,
})

-- Re-apply transparent backgrounds after every colorscheme change
-- (catppuccin sets colors_name to "catppuccin-latte"/"catppuccin-mocha" each time,
-- so these overrides must be re-applied on every reload)
vim.api.nvim_create_autocmd("ColorScheme", {
  pattern = "*",
  callback = function()
    vim.cmd([[
      hi Normal               guibg=NONE ctermbg=NONE
      hi NormalFloat          guibg=NONE ctermbg=NONE
      hi StatusLine           guibg=NONE ctermbg=NONE
      hi StatusLineNC         guibg=NONE ctermbg=NONE
      hi WinBar               guibg=NONE ctermbg=NONE
      hi WinBarNC             guibg=NONE ctermbg=NONE
      hi TabLine              guibg=NONE ctermbg=NONE
      hi TabLineFill          guibg=NONE ctermbg=NONE
      hi Folded               guibg=NONE ctermbg=NONE
    ]])
  end,
})

-- For html file recognition
vim.api.nvim_create_autocmd({ "BufRead", "BufNewFile" }, {
  pattern = {
    "*.html",
    "*.jinja",
    "*.jinja2",
    "*.html.j2",
    "*.html.jinja",
  },
  callback = function()
    -- Set the filetype to htmldjango for comprehensive Jinja/Django support
    vim.opt_local.filetype = "htmldjango"
  end,
})
