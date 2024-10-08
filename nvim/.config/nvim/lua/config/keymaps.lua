-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

-- Preview in Marked 2 App.
vim.keymap.set("n", "<leader>m", '<cmd>r!open -a "Marked 2.app" "%"<cr>', { desc = "Open in Marked2 app" })

-- Undotree
vim.keymap.set("n", "<leader>uu", require("undotree").toggle, { noremap = true, silent = true, desc = "Undotree" })

-- Toggle nvim-cmp
vim.keymap.set("n", "<leader>uj", "<cmd>lua vim.g.cmptoggle = not vim.g.cmptoggle<CR>", { desc = "Toggle nvim-cmp" })
