-- Debug warps (driven by tools/debug/warp.py, scene list tools/debug/scenes.json).
--   BLOCK = N    : dialogue viewer. Copies pointer-table entry N over entry 0 (first story dialogue, bottom box)
--                  and entry 160 (stage-1 start, top box), so a cold boot -> NEW GAME shows block N in both boxes.
--   POKES = {{addr, value16}, ...} held from POKE_FROM to POKE_TO (IWRAM/EWRAM state writes).
--   GOD = true   : keep the player's HP full (PLAYER_HP address, see docs/re/debug.md).
local TABLE = 0x7BC58C
local prg = emu.memType.gbaPrgRom
local function r32(o) return emu.read(o, prg) | emu.read(o + 1, prg) << 8 | emu.read(o + 2, prg) << 16 | emu.read(o + 3, prg) << 24 end
local function w32(o, v) for i = 0, 3 do emu.write(o + i, (v >> (8 * i)) & 0xFF, prg) end end
local done = false
L.on_frame(function(f)
  if BLOCK and not done then
    local v = r32(TABLE + 4 * BLOCK)
    w32(TABLE, v)
    w32(TABLE + 4 * 160, v)
    done = true
    L.log(string.format("block %d -> %08X (check %08X)", BLOCK, v, r32(TABLE)))
  end
  if POKES and f >= (POKE_FROM or 0) and f <= (POKE_TO or 1e9) then
    for _, p in ipairs(POKES) do emu.write16(p[1], p[2], emu.memType.gbaMemory) end
  end
  -- SCENE_ID = n at frame SCENE_AT: jump the main scene machine (byte 0x0300199A indexes the init/loop table
  -- 0x0879AC64; 22 = ending init). CHAR = 0..4 (0x03000016), PART = 0x0300007A.
  if SCENE_ID and f == (SCENE_AT or 1100) then
    if CHAR then emu.write16(0x03000016, CHAR, emu.memType.gbaMemory) end
    emu.write16(0x0300007A, PART or 0, emu.memType.gbaMemory)
    emu.write(0x0300199A, SCENE_ID, emu.memType.gbaMemory)
    L.log(string.format("scene -> %d char %s", SCENE_ID, tostring(CHAR)))
  end
  if GOD and PLAYER_HP then emu.write16(PLAYER_HP, GOD_HP or 0x60, emu.memType.gbaMemory) end
end)

-- VIEW = N: after the route, shoot every dialogue page once fully typed (reveal counter 0x03005672 ==
-- line cells 0x03005674 + 0x03005675), press A, stop after N pages.
if VIEW then
  local mem = emu.memType.gbaMemory
  local shot, stable, wait, idle = 0, 0, 0, 0
  L.on_frame(function(f)
    if not L.route_done() then return end
    if wait > 0 then wait = wait - 1; return end
    local total = emu.read(0x03005674, mem) + emu.read(0x03005675, mem)
    local rev = emu.read16(0x03005672, mem)
    if total > 0 and rev >= total then stable = stable + 1 else stable = 0 end
    if total == 0 then idle = idle + 1 else idle = 0 end
    if idle == 120 then  -- blank page (or no dialogue yet): advance without a shot
      L.press("a", 6); L.press("-", 2); idle, wait = 0, 30
      L.log(string.format("blank f%d page=%d", f, emu.read(0x03000123, mem)))
    end
    if stable == 12 then
      shot = shot + 1
      L.shot(string.format("p%03d.png", shot))
      L.log(string.format("p%03d f%d block=%08X page=%d", shot, f, emu.read32(0x0300567C, mem), emu.read(0x03000123, mem)))
      if shot >= VIEW then L.finish(0) return end
      L.press("a", 6); L.press("-", 2)
      stable, wait = 0, 30
    end
  end)
end
