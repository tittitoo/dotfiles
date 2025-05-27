-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua
-- Add any additional autocmds here

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
  pattern = { "gitcommit", "markdown", "pandoc", "norg", "*.md" },
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
