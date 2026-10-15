-- Log IWRAM game-state words every PEEK_EVERY frames (default 120): 0x03000016 stage, 0x0300007A character, + PEEK_ADDRS.
local every = PEEK_EVERY or 120
local addrs = PEEK_ADDRS or {0x03000016, 0x0300007A}
L.on_frame(function(f)
  if f % every ~= 0 then return end
  local t = {}
  for _, a in ipairs(addrs) do t[#t + 1] = string.format("%08X=%04X", a, emu.read16(a, emu.memType.gbaMemory)) end
  L.log(string.format("f%d %s", f, table.concat(t, " ")))
end)
