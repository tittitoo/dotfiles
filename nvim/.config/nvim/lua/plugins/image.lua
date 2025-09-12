return {
  "3rd/image.nvim",
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
