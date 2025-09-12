-- Disable image.nvim by default
return {
  "3rd/image.nvim",
  opts = {
    render = {
      enabled = false,
    },
  },
  config = function(opts)
    require("image").setup(opts)
  end,
}
