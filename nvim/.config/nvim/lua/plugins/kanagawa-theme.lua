return {
  "rebelot/kanagawa.nvim",
  name = "kanagawa",
  priority = 1000,
  opts = {
    transparent = true,
    theme = "dragon",
    background = {
      dark = "dragon",
      light = "lotus",
    },
    -- Explicitly set UI elements to have a transparent background.
    colors = {
      theme = {
        all = {
          ui = {
            -- Set various background highlights to transparent.
            bg_dim = "none",
            bg_p1 = "none",
            bg_p2 = "none",
            bg_m3 = "none",
            bg_gutter = "none",
            bg_search = "none",
            bg_visual = "none",
          },
        },
      },
    },
    -- Use overrides to ensure transparency for floating windows and other elements.
    overrides = function(colors)
      local theme = colors.theme
      return {
        NormalFloat = { bg = "none" },
        FloatBorder = { bg = "none" },
        Folded = { bg = "none" },
        -- Optional: Additional overrides for other plugins
        TelescopeNormal = { bg = "none" },
        -- You can add more here for plugins you use
      }
    end,
  },
  config = function(opts)
    require("kanagawa").setup(opts)
    vim.cmd("colorscheme kanagawa")
  end,
}
