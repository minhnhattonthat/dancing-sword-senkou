"""Graphics-text edits (docs/re/graphics.md). apply(rom, orig) writes every translated graphic into rom;
ranges() lists the ROM byte ranges it may write (for the romdiff test).

Graphics live in GFX_LO..GFX_HI (end of the 8 MiB ROM's 0xFF padding); text blocks stay below GFX_LO."""
import font_en

GFX_LO, GFX_HI = 0x7F0000, 0x800000

# ---- opening crawl (BG2, 4bpp, palette 4: 1 = brown, 2 = white). Loader 0x08035A92:
#  tiles  ldr r0,=0x083B6C24 (literal 0x035B5C), size movs r2,#0xD7; lsls r2,#6 (0x035A96: imm byte), dest 0x06004000
#  map    ldr r0,=0x083B9EE4 (literal 0x035B64), 0x800 bytes (32x32) -> 0x0600E000, entries 0x4000 | tile
INTRO_TILE_LIT, INTRO_COUNT_IMM, INTRO_MAP_LIT = 0x035B5C, 0x035A96, 0x035B64
INTRO_PARAS = [
    ["...At some point in time, at the far ends", "of the world, in a land between light and",
     "darkness, there came to dwell demons", "that devour the hearts of humans."],
    ["People feared them and shunned all contact,", "yet the demons appeared from nowhere,",
     "devoured them, and vanished again."],
    ["In time, people rose up and united,", "and sealed away the land the demons dwelt in..."],
    ['People called that land "the White Land."'],
    ["And now, the seal on the White Land is broken,", "and it has slowly begun to eat away at the world..."],
]
INTRO_PITCH, INTRO_GAP, INTRO_TOP, INTRO_CX = 12, 10, 4, 128


def render_lines(lines, w, h, body=2, shadow=1):
    """lines: [(text, y_top_of_cell, center_x)] -> h rows x w px of palette indices (font_en glyphs)."""
    img = [[0] * w for _ in range(h)]
    for text, y0, cx in lines:
        x = cx - font_en.text_width(text) // 2
        for ch in text:
            if ch != ' ':
                top, rows = font_en.G[ch]
                for i, r in enumerate(rows):
                    for dx, p in enumerate(r):
                        if p == '#':
                            yy = y0 + top + i
                            for sx, sy, c in ((1, 0, shadow), (0, 1, shadow), (1, 1, shadow), (0, 0, body)):
                                X, Y = x + dx + sx, yy + sy
                                if 0 <= X < w and 0 <= Y < h and (c == body or img[Y][X] != body):
                                    img[Y][X] = c
            x += font_en.width(ch)
    return img


def to_tiles(img, pal_bits=0x4000):
    """-> (tile bytes with tile 0 blank, map u16 entries row-major) deduplicating identical tiles."""
    h, w = len(img), len(img[0])
    tiles, index, entries = [bytes(32)], {bytes(32): 0}, []
    for ty in range(h // 8):
        for tx in range(w // 8):
            b = bytearray(32)
            for y in range(8):
                for x in range(8):
                    b[y * 4 + x // 2] |= img[ty * 8 + y][tx * 8 + x] << (4 * (x & 1))
            b = bytes(b)
            if b not in index:
                index[b] = len(tiles)
                tiles.append(b)
            entries.append(pal_bits | index[b])
    return b''.join(tiles), entries


def intro_image():
    lines, y = [], INTRO_TOP
    for p in INTRO_PARAS:
        for l in p:
            lines.append((l, y - font_en.Y0, INTRO_CX))
            y += INTRO_PITCH
        y += INTRO_GAP
    assert y <= 256 + INTRO_GAP, y
    return render_lines(lines, 256, 256)


# ---- character-select names (BG1, palette 11: 2 = pink, 1 = light grey). Per heroine the loader does
#  ldr r0,=tiles (-> 0x0600CC00 = tile 0x60, 0x8C0 bytes = 70 tiles), and ldr r0,=map (0x800, 32x32 -> 0x0600E000).
#  The name is the block of map cells using tiles >= 0x60; we redraw it as English rotated 90 degrees clockwise
#  (reads top to bottom): given name at 2x, family name at 1x beside it.
CS_TILE_INS = {'Kyoko': 0x0344F2, 'Claire': 0x0345BA, 'Rinrei': 0x034682, 'Mimi': 0x03474A, 'Luciel': 0x034812}
CS_MAP_LIT = {'Kyoko': 0x034554, 'Claire': 0x03461C, 'Rinrei': 0x0346E4, 'Mimi': 0x0347AC, 'Luciel': 0x0348B8}
CS_NAMES = {'Kyoko': ('Kyoko', 'Kusunoki'), 'Claire': ('Claire', 'Ludendorff'), 'Rinrei': ('Rinrei', ''),
            'Mimi': ('Mimi', ''), 'Luciel': ('Luciel', '')}
CS_TILES, CS_FIRST = 70, 0x60


def ldr_literal(rom, ins):
    hw = int.from_bytes(rom[ins:ins + 2], 'little')
    assert hw >> 11 == 0b01001, hex(hw)   # ldr rX, [pc, #imm]
    return ((ins + 4) & ~3) + (hw & 0xFF) * 4


def text_image(text, scale=1, body=2, shadow=1):
    """Horizontal text -> rows of palette indices (height 11*scale + 1, glyph rows 5..15)."""
    w = font_en.text_width(text) * scale + 1
    h = 11 * scale + 1
    img = [[0] * w for _ in range(h)]
    x = 0
    for ch in text:
        if ch != ' ':
            top, rows = font_en.G[ch]
            for i, r in enumerate(rows):
                for dx, p in enumerate(r):
                    if p != '#':
                        continue
                    for sy in range(scale):
                        for sx in range(scale):
                            X, Y = x + dx * scale + sx, (top + i) * scale + sy
                            img[Y][X] = body
                            for ox, oy in ((1, 0), (0, 1), (1, 1)):
                                if X + ox < w and Y + oy < h and img[Y + oy][X + ox] != body:
                                    img[Y + oy][X + ox] = shadow
        x += font_en.width(ch) * scale
    return img


def charselect(rom, name):
    tiles_at = int.from_bytes(rom[ldr_literal(rom, CS_TILE_INS[name]):][:4], 'little') - 0x08000000
    map_at = int.from_bytes(rom[CS_MAP_LIT[name]:CS_MAP_LIT[name] + 4], 'little') - 0x08000000
    mp = [int.from_bytes(rom[map_at + 2 * i:map_at + 2 * i + 2], 'little') for i in range(1024)]
    cells = [i for i, e in enumerate(mp) if (e & 0x3FF) >= CS_FIRST]
    pal = mp[cells[0]] & 0xF000
    x0, x1 = min(i % 32 for i in cells), max(i % 32 for i in cells)
    y0, y1 = min(i // 32 for i in cells), max(i // 32 for i in cells)
    cx = (x0 + x1 + 1) * 4                    # centre column in px
    W, H = 40, (y1 - y0 + 1) * 8              # name box: 5 tiles wide, original height
    given, family = CS_NAMES[name]
    g = text_image(given, 2)
    f = text_image(family, 1) if family else None
    # horizontal canvas (length H, thickness W): given name on top, family name under it
    canvas = [[0] * H for _ in range(W)]
    def blit(img, oy):
        ox = (H - len(img[0])) // 2
        for y, row in enumerate(img):
            for x, c in enumerate(row):
                if c and 0 <= x + ox < H and 0 <= y + oy < W:
                    canvas[y + oy][x + ox] = c
    top = (W - len(g) - (len(f) - 4 if f else 0)) // 2 - 4
    blit(g, top)
    if f:
        blit(f, top + len(g) - 6)
    # rotate 90 degrees clockwise: screen (sx, sy) = canvas[W-1-sx][sy]
    tile_px = [[canvas[W - 1 - sx][sy] for sx in range(W)] for sy in range(H)]
    new_tiles, idx, newmap = [], {}, list(mp)
    for i in cells:
        newmap[i] = 0
    bx = (cx - W // 2 + 4) // 8 * 8
    for ty in range(H // 8):
        for tx in range(W // 8):
            b = bytearray(32)
            for y in range(8):
                for x in range(8):
                    b[y * 4 + x // 2] |= tile_px[ty * 8 + y][tx * 8 + x] << (4 * (x & 1))
            b = bytes(b)
            if b == bytes(32):
                continue
            if b not in idx:
                idx[b] = CS_FIRST + len(new_tiles)
                new_tiles.append(b)
            newmap[(y0 + ty) * 32 + bx // 8 + tx] = pal | idx[b]
    assert len(new_tiles) <= CS_TILES, (name, len(new_tiles))
    old = rom[tiles_at:tiles_at + CS_TILES * 32]
    return (b''.join(new_tiles).ljust(CS_TILES * 32, b'\0'), b''.join(e.to_bytes(2, 'little') for e in newmap),
            tiles_at, map_at, old)


def build_edits(rom=None):
    if rom is None:
        from textlib import ROM
        rom = ROM.read_bytes()
    edits, at = [], GFX_LO
    for name in CS_NAMES:
        tiles, mp, _, _, _ = charselect(rom, name)
        edits += [(at, tiles), (at + len(tiles), mp),
                  (ldr_literal(rom, CS_TILE_INS[name]), (0x08000000 + at).to_bytes(4, 'little')),
                  (CS_MAP_LIT[name], (0x08000000 + at + len(tiles)).to_bytes(4, 'little'))]
        at += len(tiles) + len(mp)
    tiles, entries = to_tiles(intro_image())
    n = (len(tiles) // 32 + 1) // 2           # copy count unit = 2 tiles
    assert n <= 0xFF and len(tiles) // 32 <= 512, len(tiles) // 32
    tiles = tiles.ljust(n * 64, b'\0')
    mp = b''.join(e.to_bytes(2, 'little') for e in entries)
    assert len(mp) == 0x800
    t_at, m_at = at, at + len(tiles)
    edits += [(t_at, tiles), (m_at, mp), (INTRO_TILE_LIT, (0x08000000 + t_at).to_bytes(4, 'little')),
              (INTRO_MAP_LIT, (0x08000000 + m_at).to_bytes(4, 'little')), (INTRO_COUNT_IMM, bytes([n]))]
    at = m_at + len(mp)
    assert at <= GFX_HI
    return edits


EDITS = build_edits()


def apply(rom, orig):
    for off, data in EDITS:
        rom[off:off + len(data)] = data


def ranges():
    return [(o, o + len(d)) for o, d in EDITS]


if __name__ == '__main__':
    t, e = to_tiles(intro_image())
    print('intro tiles', len(t) // 32)
