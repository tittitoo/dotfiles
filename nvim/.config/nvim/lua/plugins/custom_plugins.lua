-- Custom plugins

return {
  {
    "folke/zen-mode.nvim",
    opts = {
      window = {
        width = 95,
      },
      plugins = {
        twilight = { enabled = false },
      },
    },
  },
  { "folke/twilight.nvim", opts = {} },
  {
    "jiaoshijie/undotree",
    dependencies = "nvim-lua/plenary.nvim",
    config = true,
    keys = { -- load the plugin only when using it's keybinding:
      { "<leader>u", "<cmd>lua require('undotree').toggle()<cr>" },
    },
  },
  -- oil-nvim
  {
    "stevearc/oil.nvim",
    opts = {},
    -- Optional dependencies
    dependencies = { { "echasnovski/mini.icons", opts = {} } },
    -- dependencies = { "nvim-tree/nvim-web-devicons" }, -- use if prefer nvim-web-devicons
  },
}
