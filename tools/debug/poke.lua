-- Hold IWRAM halfwords from frame POKE_FROM to POKE_TO: POKES = {{addr, value}, ...}
local from, to = POKE_FROM or 0, POKE_TO or 1e9
L.on_frame(function(f)
  if f < from or f > to then return end
  for _, p in ipairs(POKES or {}) do emu.write16(p[1], p[2], emu.memType.gbaMemory) end
end)
