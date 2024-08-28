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
