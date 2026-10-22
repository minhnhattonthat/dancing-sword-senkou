"""Dialogue screen tour: show every page of every dialogue block in the emulator and check the OBJ cells the VWF
drew against an independent Python rendering of the same page (tools/tour_text.lua).
  python -X utf8 tools/tour_text.py [--rom build/dancing_sword_en.gba] [--blocks N]   (exit 1 on any mismatch)
Catches lost/extra glyphs, wrong widths, paging errors and blocks that never show."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import font_en  # noqa: E402
from textlib import LINE, PAGE, all_blocks, read_block  # noqa: E402

SKILL = Path(os.environ.get(
    'SKILL', 'C:/Users/Nathan/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game'))
REC = 0xA00
GLYPHS, WIDTHS = font_en.build()


def render_line(s):
    """Mirror of asm/vwf.s: 20 cells x 0x40 bytes (8x16, two 4bpp tiles), colour 1 body, 2 shadow."""
    buf = bytearray(0x500)

    def plot(x, y, c):
        if x >= 160:
            return
        a = (x >> 3) * 0x40 + (y >> 3) * 0x20 + (y & 7) * 4 + (x & 7) // 2
        sh = 4 * (x & 1)
        buf[a] = (buf[a] & ~(0xF << sh) & 0xFF) | (c << sh)
    pen = 0
    for b in s:
        g = b - font_en.FIRST
        if g < 0 or g >= font_en.NGLYPH:
            continue
        for y in range(16):
            body = GLYPHS[g * 16 + y]
            shadow = (body << 1) & ~body
            for bits, c in ((shadow, 2), (body, 1)):
                x = 0
                while bits:
                    if bits & 1:
                        plot(pen + x, y, c)
                    bits >>= 1
                    x += 1
        pen += WIDTHS[g]
    return bytes(buf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', default=str(ROOT / 'build' / 'dancing_sword_en.gba'))
    ap.add_argument('--blocks', type=int, default=0, help='only the first N blocks (quick check)')
    ap.add_argument('--out', default=str(ROOT / 'work' / 'qa' / 'tour_text'))
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    blocks = all_blocks(rom)
    if a.blocks:
        blocks = blocks[:a.blocks]
    pages, counts = [], []
    for b in blocks:
        ps, _ = read_block(rom, b)
        n = next((i for i, p in enumerate(ps) if p[2][0] == 0xFF), len(ps))  # portrait FF also ends a dialogue
        counts.append(n)
        for l1, l2, _ in ps[:n]:
            pages.append((b, l1, l2))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    gen = out / 'blocks.lua'
    gen.write_text('BLOCKS = {%s}\n' % ', '.join('{%d, %d}' % (b, n) for b, n in zip(blocks, counts) if n))
    (out / 'tour.bin').unlink(missing_ok=True)
    frames = 1500 + len(pages) * 40
    r = subprocess.call([sys.executable, '-X', 'utf8', str(SKILL / 'scripts' / 'emu.py'), a.rom, '--out', str(out),
                         '--route', str(ROOT / 'tools' / 'routes' / 'boot.txt'), '--frames', str(frames),
                         '--timeout', str(frames // 60 + 120),
                         '--script', str(gen), '--script', str(ROOT / 'tools' / 'tour_text.lua')], cwd=ROOT)
    data = (out / 'tour.bin').read_bytes() if (out / 'tour.bin').exists() else b''
    got = len(data) // REC
    bad = []
    for i, (b, l1, l2) in enumerate(pages[:got]):
        exp = render_line(l1) + render_line(l2)
        if data[i * REC:(i + 1) * REC] != exp:
            bad.append('%06X page %d: %r / %r' % (b, i, l1, l2))
    for x in bad[:20]:
        print('MISMATCH', x)
    print('tour: %d/%d pages shown, %d mismatches (emu exit %d)' % (got, len(pages), len(bad), r))
    sys.exit(0 if got == len(pages) and not bad and r == 0 else 1)


if __name__ == '__main__':
    main()
