return {
  "lervag/vimtex",
  ft = "tex", -- Ensure VimTeX loads only for .tex files
  config = function()
    -- Set the compiler method to 'tectonic'
    vim.g.vimtex_compiler_method = "tectonic"

    -- (Optional) Configure Tectonic-specific options
    vim.g.vimtex_compiler_tectonic = {
      -- You can add options that will be passed directly to the `tectonic` command.
      -- Common options include:
      options = {
        "--synctex", -- Essential for forward/inverse search with PDF viewers
        "--keep-logs", -- Keep the log files for debugging
        -- '--outdir', 'build', -- Specify an output directory (Tectonic's --outdir is often preferred over VimTeX's global out_dir)
        -- '--keep-intermediates', -- Keep .aux, .bbl, etc.
        -- '--offline',    -- Use local caches only, don't download packages
      },
      -- 'out_dir' : '', -- VimTeX's general output directory setting. Tectonic often handles this with its own --outdir option.
      -- 'hooks' : {},   -- Advanced: run custom commands before/after compilation
    }

    -- (Optional) Configure your PDF viewer for forward/inverse search
    -- Replace 'zathura' with your preferred viewer (e.g., 'skim', 'okular', 'sumatrapdf', 'sioyek')
    vim.g.vimtex_view_method = "skim"
    -- If using a generic viewer or need specific options:
    -- vim.g.vimtex_view_general_viewer = 'your_viewer_command'
    -- vim.g.vimtex_view_general_options = '--unique file:@pdf#src:@line@tex' -- Example for a generic viewer supporting SyncTeX

    -- Other common VimTeX settings (optional but recommended for a good experience)
    -- vim.g.vimtex_quickfix_method = "pplatex" -- Or 'internal' for default log parsing
    vim.g.vimtex_syntax_enabled = 1
    vim.g.vimtex_folding_enabled = 1
    vim.g.vimtex_indent_enabled = 1
  end,
}
