return {
  {
    "bullets-vim/bullets.vim",
    lazy = false, -- Load on startup for immediate use
    config = function()
      -- Optional configuration (see plugin documentation for more options)
      vim.g.bullets_enabled = 1 -- Enable the plugin globally
      vim.g.bullets_ignore_filetypes = { "help", "gitcommit" } -- Filetypes to ignore
      vim.g.bullets_sign_priority = 10 -- Adjust sign priority if needed

      -- Define bullet levels (customize these to your preference)
      vim.g.bullets_ordered_style = "num" -- "num", "abc", "ABC", "roman", "Roman"
      vim.g.bullets_unordered_style = "dash" -- "dash", "star", "plus"
      vim.g.bullets_bullet_levels = {
        { unordered = "-", ordered = "1." },
        { unordered = "*", ordered = "a." },
        { unordered = "+", ordered = "i." },
      }

      -- Automatically renumber ordered lists on changes
      vim.g.bullets_renumber_on_change = 1

      -- Key mappings (optional, but can be useful)
      vim.keymap.set("i", "<C-t>", "<Plug>BulletedIncreaseLevel", { desc = "Increase List Level" })
      vim.keymap.set("i", "<C-d>", "<Plug>BulletedDecreaseLevel", { desc = "Decrease List Level" })
    end,
  },
}
