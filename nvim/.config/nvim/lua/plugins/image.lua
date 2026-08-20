return {
  "3rd/image.nvim",
  -- image.nvim only works over terminal graphics protocols (kitty/sixel/ueberzug),
  -- which Neovide doesn't implement since it isn't a terminal at all.
  enabled = not vim.g.neovide,
  opts = {
    integrations = {
      markdown = {
        only_render_image_at_cursor = true, -- defaults to false
        only_render_image_at_cursor_mode = "popup", -- "popup" or "inline", defaults to "popup"
      },
    },
    max_width = 100,
    max_height = 100,
  },
}
