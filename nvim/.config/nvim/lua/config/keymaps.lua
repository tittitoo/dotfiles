-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

-- Preview in Marked 2 App.
vim.keymap.set("n", "<leader>m", '<cmd>r!open -a "Marked 2.app" "%"<cr>', { desc = "Open in Marked2 app" })

-- Undotree
vim.keymap.set("n", "<leader>u", require("undotree").toggle, { noremap = true, silent = true })
