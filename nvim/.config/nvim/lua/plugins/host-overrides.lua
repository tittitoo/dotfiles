-- Per-host tweaks for machines that can't run the full config.
-- Keyed by short hostname (posonekyu.com -> posonekyu).
local host = vim.uv.os_gethostname():match("^[^.]+")

-- posonekyu: 2GB VPS on Neovim 0.11.
-- * gitcommit's parser.c is ~3MB and gcc -O2 exhausts its RAM;
--   the built-in gitcommit syntax is used instead.
-- * aerial requires Neovim >= 0.12.
local overrides = {
  posonekyu = {
    skip_parsers = { "gitcommit" },
    disable_plugins = { "stevearc/aerial.nvim" },
  },
}

local o = overrides[host] or {}
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

-- The aerial extra (from the shared lazyvim.json) still loads its telescope
-- extension and maps <leader>ss to it; stub the extension and drop the key.
if vim.tbl_contains(o.disable_plugins or {}, "stevearc/aerial.nvim") then
  package.preload["telescope._extensions.aerial"] = function()
    return {}
  end
  table.insert(specs, {
    "nvim-telescope/telescope.nvim",
    optional = true,
    keys = { { "<leader>ss", false } },
  })
end

return specs
