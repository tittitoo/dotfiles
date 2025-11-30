return {
  "iamcco/markdown-preview.nvim",
  ft = "markdown",
  config = function()
    -- This is the recommended place to set plugin-specific global variables
    vim.g.mkdp_auto_close = 0 -- Prevent preview server from shutting down when switching buffer
    vim.g.mkdp_auto_start = 0 -- Optionally prevent auto-starting

    -- ... other setup ...
  end,
}
