"""Dancing Sword - Senkou English build.
  python -X utf8 build.py build     -> build/dancing_sword_en.gba
  python -X utf8 build.py marker    -> build/dancing_sword_marker.gba (every page = [id] marker text)
  python -X utf8 build.py identity  -> rebuilds the Japanese blocks in place, asserts byte-identical
  python -X utf8 build.py release   -> release/ (BPS + README + zip)
Options: --qa ID=text (override one page's English), --out PATH, --debug (keeps nothing special; reserved)."""
import argparse
import hashlib
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'tools'))
import font_en  # noqa: E402
from asm import assemble, thumb_ldr_bx  # noqa: E402
from textlib import (EXTRA_SLOTS, LINE, PAGE, ROM, ROOT, TABLE, encode_line, load_script, paginate,  # noqa: E402
                     read_block, table_ptrs, u32)
import gfx  # noqa: E402

BUILD = ROOT / 'build'
VWF_BASE = 0x7C0000
HOOK_DRAWSTRING = 0x037184
FREE_LO, FREE_HI = 0x7C1000, gfx.GFX_LO   # 0x7BD134.. is 0xFF padding to the end of the 8 MiB ROM; gfx above
MARKER = 'The quick brown fox jumps over the lazy dog while the sword dances.'


def page_bytes(l1, l2, attr):
    p = bytearray(PAGE)
    p[0:len(l1)] = l1
    p[LINE:LINE + len(l2)] = l2
    p[0x54:0x58] = attr
    return bytes(p)


def install_vwf(rom):
    glyphs, widths = font_en.build()
    code_len = 0x100
    g_at, w_at = VWF_BASE + code_len, VWF_BASE + code_len + len(glyphs)
    code = assemble('vwf.s', 0x08000000 + VWF_BASE, {'NGLYPH': font_en.NGLYPH, 'GLYPHS': 0x08000000 + g_at,
                                                     'WIDTHS': 0x08000000 + w_at})
    assert len(code) <= code_len
    end = w_at + len(widths)
    assert end <= FREE_LO
    rom[VWF_BASE:VWF_BASE + len(code)] = code
    rom[g_at:g_at + len(glyphs)] = glyphs
    rom[w_at:w_at + len(widths)] = widths
    hook = thumb_ldr_bx(0x08000000 + HOOK_DRAWSTRING, 0x08000000 + VWF_BASE)
    rom[HOOK_DRAWSTRING:HOOK_DRAWSTRING + len(hook)] = hook


def english_of(e, byid, mode, qa):
    if e['id'] in qa:
        return qa[e['id']]
    if not any(e['jp']):
        return None
    if mode == 'marker':
        return '[%s] %s' % (e['id'], MARKER)
    src = byid[e['same_as']] if e.get('same_as') and not e['en'] else e
    return src['en']


def build_blocks(rom, orig, ents, mode, qa):
    byid = {e['id']: e for e in ents}
    blocks = {}
    for e in ents:
        blocks.setdefault(int(e['block'], 16), []).append(e)
    at = FREE_LO
    newaddr = {}
    for b, pages in sorted(blocks.items()):
        _, term = read_block(orig, b)
        out = bytearray()
        for e in pages:
            attr = bytes.fromhex(e['attr'])
            en = english_of(e, byid, mode, qa)
            if en is None:
                out += page_bytes(b'', b'', attr)
                continue
            for i, (l1, l2) in enumerate(paginate(en)):
                a = attr if i == 0 else attr[:2] + b'\0\0'   # effect bytes fire once, on the first page
                out += page_bytes(encode_line(l1), encode_line(l2), a)
        out += term
        at = (at + 3) & ~3
        if at + len(out) > FREE_HI:
            raise SystemExit('free space overflow at block %06X' % b)
        rom[at:at + len(out)] = out
        newaddr[b] = at
        at += len(out)
    for i, p in enumerate(table_ptrs(orig)):
        rom[TABLE + 4 * i:TABLE + 4 * i + 4] = (0x08000000 + newaddr[p]).to_bytes(4, 'little')
    for s in EXTRA_SLOTS:
        rom[s:s + 4] = (0x08000000 + newaddr[u32(orig, s) - 0x08000000]).to_bytes(4, 'little')
    return at


def identity(orig, ents):
    rom = bytearray(orig)
    blocks = {}
    for e in ents:
        blocks.setdefault(int(e['block'], 16), []).append(e)
    for b, pages in blocks.items():
        for n, e in enumerate(pages):
            l1, l2 = (s.encode('cp932') for s in e['jp'])
            o = b + n * PAGE
            rom[o:o + PAGE] = page_bytes(l1, l2, bytes.fromhex(e['attr']))
    return bytes(rom)


def build(mode='build', qa=None, out=None):
    orig = ROM.read_bytes()
    ents = load_script()
    rom = bytearray(orig)
    install_vwf(rom)
    end = build_blocks(rom, orig, ents, mode, qa or {})
    gfx.apply(rom, orig)
    out = Path(out or BUILD / ('dancing_sword_%s.gba' % ('marker' if mode == 'marker' else 'en')))
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(rom)
    return out, end


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['build', 'marker', 'identity', 'release'])
    ap.add_argument('--qa', action='append', default=[], help='ID=text')
    ap.add_argument('--out')
    a = ap.parse_args()
    if a.cmd == 'identity':
        orig = ROM.read_bytes()
        ok = identity(orig, load_script()) == orig
        print('identity', 'OK' if ok else 'MISMATCH')
        sys.exit(0 if ok else 1)
    if a.cmd == 'release':
        import release
        sys.exit(release.main())
    qa = dict(x.split('=', 1) for x in a.qa)
    out, end = build(a.cmd, qa, a.out)
    rom = out.read_bytes()
    print('%s  free used to 0x%06X  crc32 %08X  sha1 %s' % (out, end, zlib.crc32(rom), hashlib.sha1(rom).hexdigest()))


if __name__ == '__main__':
    main()
