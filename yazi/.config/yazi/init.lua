-- Middle-truncate filenames: show "beginning…end" instead of "beginning….ext"
-- The renderer clips the highlights child and appends whatever ellipsis() returns,
-- so returning "…FPS R0.pdf" gives middle truncation. Widths come from child.width
-- (set by redraw()) so we avoid any unavailable string-width APIs.
function Entity:ellipsis(max)
	local f = self._file

	-- Sum widths of children before highlights (id=4).
	local overhead, name_w = 0, 0
	for _, child in ipairs(self._children) do
		if child.id == 4 then
			name_w = child.width or 0
			break
		end
		overhead = overhead + (child.width or 0)
	end

	local avail = max - overhead
	if name_w <= avail then
		return nil -- fits without truncation
	end

	-- How many characters to keep from the end.
	-- ~50% of available space, bounded to [8, 25], leaving ≥5 for the start.
	local end_n = math.max(8, math.min(25, math.floor(avail * 0.5)))
	end_n = math.max(0, math.min(end_n, avail - 5))

	if end_n <= 0 then
		return "…"
	end

	-- utf8.offset(s, -n) gives the byte start of the nth-from-end character.
	local name = f.name
	local name_chars = utf8.len(name) or 0
	local end_str
	if end_n >= name_chars then
		end_str = name
	else
		local pos = utf8.offset(name, -end_n)
		end_str = pos and name:sub(pos) or name:sub(-end_n)
	end

	return "…" .. end_str
end
