# Dialogue text

- **Encoding:** Shift-JIS, fixed-length line fields. All story/stage dialogue lives in page blocks at 0x7A5144-0x7BC58B.
- **Page** = 0x58 bytes: line1[0x2A] line2[0x2A] (SJIS, NUL-padded, max 20 chars) + 4 attribute bytes:
  - +0x54 s8 portrait id (0x64 = none), +0x55 expression, +0x56 screen effect 1-7 (0 none; jump table 0x080385E0,
    fired at page start), +0x57 effect length. A page whose +0x54..55 is FF FF ends the block.
- **Pointers:** table at 0x7BC58C, 220 u32 (0x08xxxxxx) entries, 0-terminated at 0x7BC8FC; 200 unique blocks
  (story intros, stage objectives repeated at the end). Indexed by code (0x08037524: `table[char_stage + 5*[0x300007A] + 0x90]` and
  many `ldr r0,=table; ldr r0,[r0,#n]`). One more block (0x7AB7B4) is only reached from the literal 0x0802AEA4.
- **Dialogue module** 0x08037F00-0x08039200. Current block ptr 0x0300567C, page index u8 0x03000123.
  Start: 0x0803805C(r0 = block, r1). Nothing outside the module reads the page index, so adding pages is safe.
- **Renderer (original):** DrawString 0x08037184(r0 = line) -> 0x08036D60 converts SJIS to glyph ids
  (kana: sjis - 0x8240 (-0x40 above 0x833F) into font 0x084E5B24; kanji/punct: (sjis, id) table 0x087A4A5C into font
  0x08636A04), 0x08036C80 copies 8x16 4bpp cells (0x40 bytes) to OBJ VRAM [0x0300547C] (line1 0x06017000,
  line2 0x06017500, 20 cells each), returns char count (0x0803719C) = number of OBJ cells the typewriter reveals.
  Colours: 1 = ink, 2 = light shadow to the right.
- **English renderer:** `asm/vwf.s` at 0x087C0000 replaces DrawString (hook `ldr r1,=vwf; bx r1` at 0x08037184).
  ASCII 0x20-0x7E + extras 0x80-0x83 (font `tools/font_en.py`), proportional, 160 px/line, returns cells used.
- **Relocation:** the build writes every block (re-paginated: 2 lines/page, extra pages copy portrait bytes and zero the
  effect bytes) into 0x7C1000-0x7FFFFF (0xFF padding of the 8 MiB ROM) and repoints the table + 0x2AEA4.
- Width gate: both box variants (story box at the bottom, in-stage box at the top) are 20 cells = 160 px x 2 lines.
