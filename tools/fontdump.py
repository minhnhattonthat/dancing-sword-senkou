"""Render the game's dialogue font (8x16 4bpp cells at 0x4E5B24, index = SJIS - 0x8240, -0x40 above 0x833F) to a PNG.
usage: python -X utf8 tools/fontdump.py ROM OUT.png [first_sjis last_sjis]"""
import sys, struct, zlib

FONT = 0x4E5B24


def glyph_index(sj):
    g = sj - 0x8240
    return g - 0x40 if sj > 0x833F else g


def cell(rom, idx):
    """16 rows x 8 px of palette indices."""
    b = rom[FONT + idx * 0x40: FONT + idx * 0x40 + 0x40]
    rows = []
    for t in range(2):
        for r in range(8):
            w = b[t * 32 + r * 4: t * 32 + r * 4 + 4]
            rows.append([(w[x >> 1] >> (4 * (x & 1))) & 15 for x in range(8)])
    return rows


def png(path, w, h, px):  # px: rows of grey levels 0-255
    raw = b''.join(b'\x00' + bytes(r) for r in px)
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d))
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0))
                           + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read()
    lo, hi = (int(sys.argv[3], 16), int(sys.argv[4], 16)) if len(sys.argv) > 4 else (0x8240, 0x829A)
    codes = [c for c in range(lo, hi + 1) if (c & 0xFF) != 0x7F]
    cols, z = 16, 4
    rows_n = (len(codes) + cols - 1) // cols
    W, H = cols * 9 * z, rows_n * 17 * z
    img = [[40] * W for _ in range(H)]
    for i, c in enumerate(codes):
        cx, cy = (i % cols) * 9, (i // cols) * 17
        for y, row in enumerate(cell(rom, glyph_index(c))):
            for x, v in enumerate(row):
                for dy in range(z):
                    for dx in range(z):
                        img[(cy + y) * z + dy][(cx + x) * z + dx] = 255 - v * 16 if v else 200
    png(sys.argv[2], W, H, img)
