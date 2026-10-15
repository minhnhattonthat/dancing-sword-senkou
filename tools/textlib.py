"""Dialogue data layout (docs/re/text.md) and the English layout rules shared by extract / build / lint."""
import json
import struct
from pathlib import Path

import font_en

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / 'rom' / 'Dancing Sword - Senkou (Japan).gba'
SCRIPT = ROOT / 'script'

TABLE = 0x7BC58C          # u32 block pointers, 0-terminated (220 entries, 200 unique blocks)
TABLE_END = 0x7BC8FC
EXTRA_SLOTS = [0x2AEA4]   # code literal-pool words pointing at a block outside the table
PAGE = 0x58               # line1[42] line2[42] portrait(s8) expression effect effect_len
LINE = 0x2A               # 41 chars + NUL
LINE_PX = 160             # 20 OBJ cells of 8 px (measured: 0x500 bytes of cells per line)
LINES_PER_PAGE = 2
END_ATTR = b'\xff\xff'


def u32(d, a):
    return struct.unpack_from('<I', d, a)[0]


def table_ptrs(d):
    out, a = [], TABLE
    while u32(d, a):
        out.append(u32(d, a) - 0x08000000)
        a += 4
    assert a == TABLE_END
    return out


def all_blocks(d):
    """-> sorted unique block offsets (table + extra slots)."""
    return sorted(set(table_ptrs(d)) | {u32(d, s) - 0x08000000 for s in EXTRA_SLOTS})


def read_block(d, off):
    """-> (pages [(raw_line1, raw_line2, attr4)], terminator_page_bytes)."""
    pages = []
    while d[off + 0x54:off + 0x56] != END_ATTR:
        p = d[off:off + PAGE]
        pages.append((p[:LINE].split(b'\0')[0], p[LINE:2 * LINE].split(b'\0')[0], p[0x54:0x58]))
        off += PAGE
    return pages, d[off:off + PAGE]


def sjis(b):
    return b.decode('cp932')


def load_script():
    """-> list of entries from script/*.json in file order."""
    ents = []
    for f in sorted(SCRIPT.glob('*.json')):
        ents.extend(json.loads(f.read_text(encoding='utf-8')))
    return ents


def save_json(path, obj):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write('\n')


def encode_line(s):
    out = bytearray()
    for ch in s:
        if not font_en.encodable(ch):
            raise ValueError('unencodable %r in %r' % (ch, s))
        out.append(font_en.code_of(ch))
    if len(out) >= LINE:
        raise ValueError('line over %d bytes: %r' % (LINE - 1, s))
    return bytes(out)


def wrap(text, px=LINE_PX):
    """Greedy-then-balanced wrap into lines of <= px. Explicit '\\n' forces a break. -> list of lines."""
    lines = []
    for para in text.split('\n'):
        words = para.split(' ')
        cur = ''
        for w in words:
            cand = w if not cur else cur + ' ' + w
            if font_en.text_width(cand) <= px:
                cur = cand
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def paginate(text):
    """English for one original page -> list of pages, each [line1, line2]."""
    lines = wrap(text)
    # balance a final page holding one short line after a full page: pull nothing, keep simple
    pages = [lines[i:i + LINES_PER_PAGE] for i in range(0, len(lines), LINES_PER_PAGE)]
    return [p + [''] * (LINES_PER_PAGE - len(p)) for p in pages] or [['', '']]
