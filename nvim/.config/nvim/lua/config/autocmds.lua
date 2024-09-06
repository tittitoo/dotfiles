-- Autocmds are automatically loaded on the VeryLazy event
-- Default autocmds that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/autocmds.lua
-- Add any additional autocmds here
--

-- disable completion on markdown files by default
-- vim.api.nvim_create_autocmd("FileType", {
--   pattern = { "gitcommit", "markdown" },
--   callback = function()
--     require("cmp").setup({ enabled = false })
--   end,
-- })

-- Set textwidth to 80 and automatic line breaks for markdown files
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "gitcommit", "markdown", "pandoc" },
  callback = function()
    require("cmp").setup({ enabled = false })
    vim.opt_local.textwidth = 80
    -- vim.opt_local.formatoptions:append("a")
    -- vim.opt_local.colorcolumn = "80"
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

-- Define a function to save the file
local function auto_save()
  if vim.bo.filetype == "markdown" then
    vim.cmd("silent! wa")
  end
end

-- Set up an autocmd to trigger the function after typing has stopped
vim.api.nvim_create_augroup("AutoSaveGroup", { clear = true })
vim.api.nvim_create_autocmd({ "TextChanged", "TextChangedI" }, {
  group = "AutoSaveGroup",
  pattern = "*",
  callback = auto_save,
})
