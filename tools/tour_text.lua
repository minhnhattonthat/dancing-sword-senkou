-- Dialogue screen tour (driven by tools/tour_text.py, which prepends BLOCKS = {{rom_off, pages}, ...}).
-- Cold boot -> first story dialogue (pointer-table entry 0 is aimed at BLOCKS[1]); then every page of every block
-- is shown in turn: when the last page of a block is up, the block pointer 0x0300567C is re-aimed so the next A
-- lands on page 0 of the next block. Typing is skipped (reveal counter 0x03005672 = cells). For each page the
-- 0xA00 bytes of OBJ cells (line 1 0x06017000, line 2 0x06017500) go to OUT/tour.bin, one record per page,
-- and a log line "page <n> <block> <page>".
local mem, prg, vram = emu.memType.gbaMemory, emu.memType.gbaPrgRom, emu.memType.gbaVideoRam
local TABLE = 0x7BC58C
local function w32(o, v) for i = 0, 3 do emu.write(o + i, (v >> (8 * i)) & 0xFF, prg) end end
w32(TABLE, 0x08000000 + BLOCKS[1][1])
local out = assert(io.open(OUT .. "tour.bin", "wb"))
local bi, pg, n, wait, lastidx, settle = 1, 0, 0, 0, -1, 0
local started = false
L.on_frame(function(f)
  if not L.route_done() then return end
  if wait > 0 then wait = wait - 1; return end
  local ptr = emu.read32(0x0300567C, mem)
  local idx = emu.read(0x03000123, mem)
  if not started then
    if ptr ~= 0x08000000 + BLOCKS[1][1] then return end
    started = true; lastidx = -1
  end
  if idx == lastidx then
    settle = settle + 1
    if settle > 600 then L.log("STUCK at block " .. bi .. " page " .. pg); L.finish(4) end
    return
  end
  -- a new page is up: let the draw finish, skip typing, dump
  if settle < 3 then settle = settle + 1; return end
  local total = emu.read(0x03005674, mem) + emu.read(0x03005675, mem)
  emu.write16(0x03005672, total, mem)
  local t = {}
  for a = 0x17000, 0x179FF do t[#t + 1] = string.char(emu.read(a, vram)) end
  out:write(table.concat(t))
  n = n + 1
  L.log(string.format("page %d %06X %d f%d", n, BLOCKS[bi][1], pg, f))
  lastidx, settle = idx, 0
  pg = pg + 1
  if pg >= BLOCKS[bi][2] then
    bi = bi + 1; pg = 0
    if bi > #BLOCKS then out:close(); L.log("DONE " .. n); L.finish(0); return end
    -- next A: idx 0 -> 1 = page 0 of the next block (reset idx so the u8 never wraps)
    emu.write(0x03000123, 0, mem)
    emu.write32(0x0300567C, 0x08000000 + BLOCKS[bi][1] - 0x58, mem)
    lastidx = 0
  end
  L.press("-", 2); L.press("a", 4); L.press("-", 4)
  wait = 8
end)
