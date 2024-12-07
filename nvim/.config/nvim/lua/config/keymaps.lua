-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

-- Preview in Marked 2 App.
vim.keymap.set("n", "<leader>m", '<cmd>r!open -a "Typora.app" "%"<cr>', { desc = "Open in Typora app" })

-- Undotree
vim.keymap.set("n", "<leader>uu", require("undotree").toggle, { noremap = true, silent = true, desc = "Undotree" })

-- Toggle nvim-cmp
vim.keymap.set("n", "<leader>uj", "<cmd>lua vim.g.cmptoggle = not vim.g.cmptoggle<CR>", { desc = "Toggle nvim-cmp" })

-- oil.nvim
vim.keymap.set("n", "-", "<cmd>Oil<CR>", { desc = "Open parent directory" })

-- Split Window Below
vim.keymap.set("n", '<leader>"', "<cmd>split<CR>", { noremap = false, silent = true, desc = "Split Window Below" })

-- Zen Mode
vim.keymap.set("n", "<leader>z", "<cmd>ZenMode<CR>", { desc = "ZenMode" })

-- Neorg core.text-objects keymap
vim.keymap.set("n", "<up>", "<Plug>(neorg.text-objects.item-up)", {})
vim.keymap.set("n", "<down>", "<Plug>(neorg.text-objects.item-down)", {})
vim.keymap.set({ "o", "x" }, "iH", "<Plug>(neorg.text-objects.textobject.heading.inner)", {})
vim.keymap.set({ "o", "x" }, "aH", "<Plug>(neorg.text-objects.textobject.heading.outer)", {})
