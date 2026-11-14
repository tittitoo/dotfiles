local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local lazyrepo = "https://github.com/folke/lazy.nvim.git"
  local out = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", lazyrepo, lazypath })
  if vim.v.shell_error ~= 0 then
    vim.api.nvim_echo({
      { "Failed to clone lazy.nvim:\n", "ErrorMsg" },
      { out, "WarningMsg" },
      { "\nPress any key to exit..." },
    }, true, {})
    vim.fn.getchar()
    os.exit(1)
  end
end
vim.opt.rtp:prepend(lazypath)

-- Lite profile for small boxes used only to edit config files: listed hosts,
-- or any machine started with NVIM_LITE=1 (e.g. `set -Ux NVIM_LITE 1` in fish).
local lite_hosts = { "posonekyu" }
vim.g.nvim_lite = vim.env.NVIM_LITE == "1"
  or vim.tbl_contains(lite_hosts, vim.uv.os_gethostname():match("^[^.]+"))

-- Lite machines disable some plugins (see config/host-overrides.lua), so a
-- :Lazy update/sync there would drop them from the synced lockfile. Give them
-- a private copy, refreshed from the shared one on every start, so :Lazy
-- restore still follows the shared pins but nothing is ever written back.
local lockfile = vim.fn.stdpath("config") .. "/lazy-lock.json"
if vim.g.nvim_lite then
  local private = vim.fn.stdpath("state") .. "/lazy-lock.json"
  vim.uv.fs_copyfile(lockfile, private)
  lockfile = private
  -- Config-editing box: a trimmed extras list instead of the full dev set
  -- (no language servers, test runners, AI, animations). :LazyExtras there
  -- edits this file, leaving the shared lazyvim.json alone.
  vim.g.lazyvim_json = vim.fn.stdpath("config") .. "/lazyvim-lite.json"
end

require("lazy").setup({
  lockfile = lockfile,
  spec = {
    -- add LazyVim and import its plugins
    { "LazyVim/LazyVim", import = "lazyvim.plugins" },
    -- import/override with your plugins
    { import = "plugins" },
    -- per-host overrides go last so they win over any plugins/*.lua spec
    { import = "config.host-overrides" },
  },
  defaults = {
    -- By default, only LazyVim plugins will be lazy-loaded. Your custom plugins will load during startup.
    -- If you know what you're doing, you can set this to `true` to have all your custom plugins lazy-loaded by default.
    lazy = false,
    -- It's recommended to leave version=false for now, since a lot the plugin that support versioning,
    -- have outdated releases, which may break your Neovim install.
    version = false, -- always use the latest git commit
    -- version = "*", -- try installing the latest stable version for plugins that support semver
  },
  install = { colorscheme = { "tokyonight", "habamax" } },
  checker = { enabled = true }, -- automatically check for plugin updates
  performance = {
    rtp = {
      -- disable some rtp plugins
      disabled_plugins = {
        "gzip",
        -- "matchit",
        -- "matchparen",
        -- "netrwPlugin",
        "tarPlugin",
        "tohtml",
        "tutor",
        "zipPlugin",
      },
    },
  },
})
