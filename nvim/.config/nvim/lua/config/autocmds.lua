-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua
-- Add any additional autocmds here

-- initialize global var to false -> nvim-cmp turned off by default
vim.g.cmptoggle = true

require("cmp").setup({
  enabled = function()
    return vim.g.cmptoggle
  end,
})
-- wrap and check for spell in text filetypes
-- added to disable spelling
vim.api.nvim_create_autocmd("FileType", {
  -- group = augroup("wrap_spell"),
  pattern = { "gitcommit", "markdown", "pandoc" },
  callback = function()
    vim.opt_local.wrap = true
    vim.opt_local.spell = false
    vim.opt_local.textwidth = 80
  end,
})

vim.api.nvim_create_autocmd("filetype", {
  -- group = augroup("wrap_spell"),
  pattern = { "gitcommit", "markdown", "pandoc" },
  command = "set nospell",
})

-- Automatically save file when switching buffers or losing focus
-- Meant for Marked2 preview
vim.api.nvim_create_augroup("auto_save", { clear = true })
vim.api.nvim_create_autocmd("BufLeave", {
  group = "auto_save",
  pattern = "*",
  command = "silent! wa",
})
vim.api.nvim_create_autocmd("FocusLost", {
  group = "auto_save",
  pattern = "*",
  command = "silent! wa",
})

-- -- Define a function to save the file
-- local function auto_save()
--   if vim.bo.filetype == "markdown" then
--     vim.cmd("silent! wa")
--   end
-- end
--
-- -- Set up an autocmd to trigger the function after typing has stopped
-- vim.api.nvim_create_augroup("AutoSaveGroup", { clear = true })
-- vim.api.nvim_create_autocmd({ "TextChanged", "TextChangedI" }, {
--   group = "AutoSaveGroup",
--   pattern = "*",
--   callback = auto_save,
-- })
