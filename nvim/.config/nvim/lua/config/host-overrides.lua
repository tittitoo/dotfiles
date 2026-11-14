-- Overrides for machines that can't run the full config: the "lite" profile
-- (vim.g.nvim_lite, set in config/lazy.lua) plus per-host extras keyed by
-- short hostname (posonekyu.com -> posonekyu).
local host = vim.uv.os_gethostname():match("^[^.]+")

-- lite: small boxes used only to edit config files. Runs LazyVim's core UI
-- with the extras in lazyvim-lite.json; this drops the personal plugins that
-- only make sense on the Mac or for programming.
-- * auto-dark-mode spawns dbus-send every 3s with no desktop to answer it;
--   catppuccin follows the terminal's background instead.
-- * Mason auto-enables every installed server, so on a new lite machine
--   only lua-language-server, stylua, shellcheck and shfmt should be there.
local lite = {
  disable_plugins = {
    "f-person/auto-dark-mode.nvim",
    "rebelot/kanagawa.nvim",
    "supermaven-inc/supermaven-nvim",
    "jalvesaq/zotcite",
    "lervag/vimtex",
    "iamcco/markdown-preview.nvim",
    "3rd/image.nvim",
  },
  disable_servers = { "markdown_oxide", "tailwindcss", "bashls" },
  skip_mason = { "markdown-oxide" },
  follow_background = true,
}

-- posonekyu: 1-CPU 2GB VPS on Neovim 0.11.
-- * gitcommit's parser.c is ~3MB and gcc -O2 exhausts its RAM;
--   the built-in gitcommit syntax is used instead.
local overrides = {
  posonekyu = {
    skip_parsers = { "gitcommit" },
  },
}

local o = vim.tbl_extend("force", vim.g.nvim_lite and lite or {}, overrides[host] or {})
local skip = o.skip_parsers or {}

local specs = {
  {
    "nvim-treesitter/nvim-treesitter",
    opts = function(_, opts)
      if #skip > 0 then
        opts.ensure_installed = vim.tbl_filter(function(lang)
          return not vim.tbl_contains(skip, lang)
        end, opts.ensure_installed or {})
      end
    end,
  },
}

for _, name in ipairs(o.disable_plugins or {}) do
  table.insert(specs, { name, enabled = false })
end

if o.disable_servers then
  table.insert(specs, {
    "neovim/nvim-lspconfig",
    opts = function(_, opts)
      opts.servers = opts.servers or {}
      for _, server in ipairs(o.disable_servers) do
        opts.servers[server] = false
      end
    end,
  })
end

if o.skip_mason then
  table.insert(specs, {
    "mason-org/mason.nvim",
    opts = function(_, opts)
      opts.ensure_installed = vim.tbl_filter(function(pkg)
        return not vim.tbl_contains(o.skip_mason, pkg)
      end, opts.ensure_installed or {})
    end,
  })
end

-- custom_plugins.lua tunes blink's supermaven provider; without the plugin
-- that leaves a provider with no module behind.
if vim.tbl_contains(o.disable_plugins or {}, "supermaven-inc/supermaven-nvim") then
  table.insert(specs, {
    "saghen/blink.cmp",
    opts = function(_, opts)
      if opts.sources and opts.sources.providers then
        opts.sources.providers.supermaven = nil
      end
    end,
  })
end

if o.follow_background then
  table.insert(specs, {
    "catppuccin/nvim",
    name = "catppuccin",
    opts = { flavour = "auto", background = { light = "latte", dark = "mocha" } },
  })
end

return specs
