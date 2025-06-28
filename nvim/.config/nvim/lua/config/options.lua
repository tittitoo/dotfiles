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

-- Enable AI completion
vim.g.ai_cmp = true

-- Disable swap file. Take the risk
vim.opt.swapfile = false

-- Default python path
vim.g.python3_host_prog = vim.fn.expand("~/Repos/github.com/tittitoo/nvim-python/.venv/bin/python3")

-- Disable image preview by default
-- To evaluate if it works
vim.g.enable_image_preview = false
