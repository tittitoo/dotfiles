-- Note-creation commands for the dragon vault.
-- Each fills in the boilerplate (filename pattern, date, tag placement)
-- so naming/tagging discipline doesn't have to be held in memory.

local function slugify(str)
  local slug = str:lower():gsub("[^%w]+", "-")
  slug = slug:gsub("^%-+", ""):gsub("%-+$", "")
  return slug
end

-- Opens `path`, and if it's a new file, seeds it with `lines` and writes
-- it immediately so the note exists on disk right away.
local function new_note(path, lines)
  vim.cmd.edit(vim.fn.fnameescape(path))
  if vim.fn.filereadable(path) == 0 then
    vim.api.nvim_buf_set_lines(0, 0, -1, false, lines)
    vim.cmd.write()
  end
  vim.api.nvim_win_set_cursor(0, { vim.api.nvim_buf_line_count(0), 0 })
end

vim.api.nvim_create_user_command("Minutes", function(opts)
  if opts.args == "" then
    vim.notify("Usage: :Minutes <party>", vim.log.levels.ERROR)
    return
  end
  local date = os.date("%Y-%m-%d")
  local path = vim.fn.getcwd() .. "/minutes-" .. slugify(opts.args) .. "-" .. date .. ".md"
  new_note(path, { "# Minutes " .. opts.args .. " " .. date, "", "tags:", "#minutes", "" })
end, { nargs = "+", desc = "Create minutes-<party>-<date>.md tagged #minutes" })

vim.api.nvim_create_user_command("Literature", function(opts)
  if opts.args == "" then
    vim.notify("Usage: :Literature <title>", vim.log.levels.ERROR)
    return
  end
  local path = vim.fn.getcwd() .. "/" .. slugify(opts.args) .. ".md"
  new_note(path, { "# " .. opts.args, "", "tags:", "#literature", "" })
end, { nargs = "+", desc = "Create a literature note tagged #literature" })

vim.api.nvim_create_user_command("Dragon", function(opts)
  if opts.args == "" then
    vim.notify("Usage: :Dragon <title>", vim.log.levels.ERROR)
    return
  end
  local path = vim.fn.getcwd() .. "/" .. slugify(opts.args) .. ".md"
  new_note(path, { "# " .. opts.args, "", "tags:", "#dragon", "" })
end, { nargs = "+", desc = "Create an atomic/permanent note tagged #dragon" })

-- markdown-oxide's daily-note command. Not registered automatically by the
-- LSP client, per markdown-oxide's own setup docs -- this wires it up.
-- Usage: :Daily today | :Daily next monday | :Daily 2 days ago
vim.api.nvim_create_user_command("Daily", function(opts)
  vim.lsp.buf.execute_command({ command = "jump", arguments = { opts.args } })
end, { nargs = "*", desc = "Open a daily note (markdown-oxide)" })
