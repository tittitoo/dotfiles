-- Neorg config
return {
  "nvim-neorg/neorg",
  lazy = false, -- Disable lazy loading as some `lazy.nvim` distributions set `lazy = true` by default
  version = "*", -- Pin Neorg to the latest stable release
  -- config = true,
  config = function()
    require("neorg").setup({
      load = {
        ["core.defaults"] = {}, -- Loads default behaviour
        ["core.concealer"] = {}, -- Adds pretty icons to your documents
        ["core.ui.calendar"] = {},
        ["core.completion"] = { config = { engine = "nvim-cmp", name = "[Neorg]", sources = "neorg" } },
        ["core.integrations.nvim-cmp"] = {},
        -- ["core.concealer"] = { config = { icon_preset = "diamond" } },
        ["core.esupports.metagen"] = {
          config = {
            author = "Thiha Aung",
            -- timezone = "implicit-local",
            type = "auto",
            update_date = true,
          },
        },
        ["core.qol.toc"] = {},
        ["core.qol.todo_items"] = {},
        ["core.looking-glass"] = {},
        ["core.presenter"] = { config = { zen_mode = "zen-mode" } },
        ["core.export"] = {},
        ["core.export.markdown"] = { config = { extensions = "all" } },
        ["core.summary"] = {},
        ["core.tangle"] = { config = { report_on_empty = false } },
        ["core.text-objects"] = {},
        ["core.dirman"] = { -- Manages Neorg workspaces
          config = {
            workspaces = {
              dragon = "~/Repos/github.com/tittitoo/dragon",
              notes = "~/Documents/Notes",
            },
            default_workspace = "dragon",
          },
        },
        ["core.dirman.utils"] = {},
        ["core.integrations.treesitter"] = {},
      },
    })
  end,
}
