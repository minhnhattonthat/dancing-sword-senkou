import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build  # noqa: E402
import font_en  # noqa: E402
from textlib import PAGE, ROM, TABLE, TABLE_END, EXTRA_SLOTS, all_blocks, load_script, read_block  # noqa: E402

ORIG = ROM.read_bytes()
KANA = re.compile(rb'(?:[\x81-\x84\x88-\x9f\xe0-\xea][\x40-\xfc]){3,}')


def test_identity():
    assert build.identity(ORIG, load_script()) == ORIG


def test_coverage():
    """Every SJIS run with kana between the first and last block lies inside an extracted page."""
    covered = set()
    for b in all_blocks(ORIG):
        pages, _ = read_block(ORIG, b)
        covered.update(range(b, b + (len(pages) + 1) * PAGE))
    lo, hi = min(covered), max(covered)
    miss = []
    for m in KANA.finditer(ORIG, lo, hi):
        t = m.group().decode('cp932', 'replace')
        if re.search('[぀-ヿ]', t) and m.start() not in covered:
            miss.append(hex(m.start()))
    assert not miss


def test_font():
    g, w = font_en.build()
    assert len(g) == 16 * font_en.NGLYPH
    assert all(w[ord(c) - font_en.FIRST] for c in ''.join(chr(i) for i in range(0x20, 0x7F)))


@pytest.fixture(scope='module')
def built(tmp_path_factory):
    out, end = build.build('build', out=tmp_path_factory.mktemp('b') / 'en.gba')
    return out.read_bytes(), end


def test_build_writes_only_allowed(built):
    rom, end = built
    allowed = [(build.HOOK_DRAWSTRING, build.HOOK_DRAWSTRING + 8), (TABLE, TABLE_END), (build.VWF_BASE, end)]
    allowed += [(s, s + 4) for s in EXTRA_SLOTS] + build.gfx.ranges()
    bad = [i for i in range(len(ORIG)) if rom[i] != ORIG[i] and not any(a <= i < b for a, b in allowed)]
    assert not bad, hex(bad[0])


def test_build_blocks_readable(built):
    rom, _ = built
    for b in all_blocks(rom):
        pages, _ = read_block(rom, b)
        assert pages
