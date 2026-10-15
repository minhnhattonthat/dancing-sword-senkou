"""Title screen BG3 (8bpp, tiles raw at ROM 0x3440E4 + VRAM offset, map 0x34B864, palette = BG palette).
Helpers to read/write the logo region as pixels. python -X utf8 tools/title_gfx.py OUT.png -> zoomed crop for inspection."""
import struct
import sys

TILES, MAP = 0x3440E4, 0x34B864


def entries(rom):
    return [struct.unpack_from('<H', rom, MAP + 2 * i)[0] for i in range(32 * 32)]


def get_px(rom, x, y):
    e = entries_cache(rom)[(y // 8) * 32 + x // 8]
    t = e & 0x3FF
    return rom[TILES + t * 64 + (y % 8) * 8 + x % 8]


_cache = {}


def entries_cache(rom):
    k = id(rom)
    if k not in _cache:
        _cache[k] = entries(rom)
    return _cache[k]


def set_px(rom, x, y, v):
    e = entries_cache(rom)[(y // 8) * 32 + x // 8]
    rom[TILES + (e & 0x3FF) * 64 + (y % 8) * 8 + x % 8] = v


def tile_uses(rom):
    from collections import Counter
    return Counter(e & 0x3FF for e in entries(rom))


if __name__ == '__main__':
    sys.path.insert(0, __file__.rsplit('\\', 1)[0])
    from textlib import ROM
    from fontdump import png
    rom = ROM.read_bytes()
    x0, y0, w, h, z = 40, 28, 200, 32, 4
    img = []
    for y in range(h):
        row = []
        for x in range(w):
            v = get_px(rom, x0 + x, y0 + y)
            row += [v] * z
        img += [row] * z
    png(sys.argv[1], w * z, h * z, img)
