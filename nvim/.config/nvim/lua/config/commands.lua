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
  new_note(path, { "# Minutes " .. opts.args .. " " .. date, "", "tags:", "#minutes", "", "" })
end, { nargs = "+", desc = "Create minutes-<party>-<date>.md tagged #minutes" })

vim.api.nvim_create_user_command("Lit", function(opts)
  if opts.args == "" then
    vim.notify("Usage: :Lit <title>", vim.log.levels.ERROR)
    return
  end
  local path = vim.fn.getcwd() .. "/" .. slugify(opts.args) .. ".md"
  new_note(path, { "# " .. opts.args, "", "tags:", "#literature", "", "" })
end, { nargs = "+", desc = "Create a literature note tagged #literature" })

vim.api.nvim_create_user_command("Dragon", function(opts)
  if opts.args == "" then
    vim.notify("Usage: :Dragon <title>", vim.log.levels.ERROR)
    return
  end
  local path = vim.fn.getcwd() .. "/" .. slugify(opts.args) .. ".md"
  new_note(path, { "# " .. opts.args, "", "tags:", "#dragon", "", "" })
end, { nargs = "+", desc = "Create an atomic/permanent note tagged #dragon" })

-- markdown-oxide's daily-note command. Not registered automatically by the
-- LSP client, per markdown-oxide's own setup docs -- this wires it up.
-- Usage: :Daily today | :Daily next monday | :Daily 2 days ago
vim.api.nvim_create_user_command("Daily", function(opts)
  vim.lsp.buf.execute_command({ command = "jump", arguments = { opts.args } })
end, { nargs = "*", desc = "Open a daily note (markdown-oxide)" })

-- Renames the current note and rewrites every [[wikilink]] reference to it
-- across the vault, via scripts/.config/scripts/note-rename -- the
-- sanctioned rename path (plain file rename and markdown-oxide's own LSP
-- rename don't reliably update backlinks; the latter renames the wrong
-- file when triggered from an inbound link rather than the target note).
-- Feeds the new slug over stdin so the script's interactive prompt
-- doesn't need a terminal here.
vim.api.nvim_create_user_command("Rename", function(opts)
  if opts.args == "" then
    vim.notify("Usage: :Rename <new title>", vim.log.levels.ERROR)
    return
  end
  local path = vim.api.nvim_buf_get_name(0)
  if not path:match("%.md$") then
    vim.notify(":Rename only works on markdown notes", vim.log.levels.ERROR)
    return
  end
  vim.cmd.write()
  -- Strip a trailing ".md" the user typed out of file-rename muscle
  -- memory (case-insensitive) -- slugify() would otherwise turn it into a
  -- literal "-md" suffix on the slug, same bug this command exists to fix.
  local title = opts.args:gsub("%.[Mm][Dd]$", "")
  local new_slug = slugify(title)
  local result = vim.fn.system({ "note-rename", path }, new_slug .. "\n")
  if vim.v.shell_error ~= 0 then
    vim.notify("Rename failed:\n" .. result, vim.log.levels.ERROR)
    return
  end
  vim.notify(result)
  local old_buf = vim.api.nvim_get_current_buf()
  local dir = vim.fn.fnamemodify(path, ":h")
  vim.cmd.edit(vim.fn.fnameescape(dir .. "/" .. new_slug .. ".md"))
  -- Without this, the old buffer lingers pointing at a path that no
  -- longer exists on disk (harmless but confusing in :ls/bufferline).
  vim.api.nvim_buf_delete(old_buf, { force = true })
end, { nargs = "+", desc = "Rename this note and fix [[links]] to it vault-wide" })
