-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

-- Disable line numbers
vim.opt.number = false -- Disable line numbers
vim.opt.relativenumber = false -- Disable relative line numbers

-- Set tab to 4 spaces
vim.opt.tabstop = 4 -- Number of spaces that a <Tab> counts for
vim.opt.shiftwidth = 4 -- Number of spaces to use for each step of (auto)indent
vim.opt.expandtab = true -- Use spaces instead of tabs

-- Enable Codeium status
vim.g.codeium_enabled = true

-- Turn off ai completions. It will be shown as ghost text.
-- Otherwise, it will show all the options to choose from which could be noisy.
vim.g.ai_cmp = false
