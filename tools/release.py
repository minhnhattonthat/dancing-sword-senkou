"""Release gate + package: lint --strict -> tests -> build -> smoke -> jp_left (slots) -> BPS make/verify -> README
-> release/dancing-sword-senkou_en.zip (patch + README). --no-tour skips the dialogue screen tour (tools/tour_text.py).
Never publishes anything."""
import hashlib
import os
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = Path(os.environ.get(
    'SKILL', 'C:/Users/Nathan/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game'))
sys.path.insert(0, str(ROOT / 'tools'))
from textlib import EXTRA_SLOTS, ROM, TABLE, TABLE_END  # noqa: E402

VERSION = '1.0'
SLUG = 'dancing-sword-senkou'
PATCH = 'Dancing_Sword_Senkou_EN_v%s.bps' % VERSION
PY = [sys.executable, '-X', 'utf8']


def run(cmd, what):
    print('==', what, flush=True)
    r = subprocess.call(cmd, cwd=ROOT)
    if r:
        sys.exit('release gate failed at: %s (exit %d)' % (what, r))


def hashes(b):
    return '%08X' % zlib.crc32(b), hashlib.md5(b).hexdigest(), hashlib.sha1(b).hexdigest()


def main():
    tour = '--no-tour' not in sys.argv
    run(PY + ['tools/lint.py', '--strict'], 'lint')
    run(PY + ['-m', 'pytest', '-q', 'tests'], 'tests')
    run(PY + ['build.py', 'build'], 'build')
    built = ROOT / 'build' / 'dancing_sword_en.gba'
    run(PY + [str(SKILL / 'scripts' / 'emu.py'), str(built), '--out', 'work/qa/release_smoke', '--route',
              'tools/routes/boot.txt', '--smoke'], 'smoke')
    slots = ROOT / 'work' / 'slots.txt'
    slots.write_text('\n'.join('%X' % a for a in list(range(TABLE, TABLE_END, 4)) + EXTRA_SLOTS) + '\n')
    run(PY + [str(SKILL / 'scripts' / 'jp_left.py'), str(built), '--sjis', '--slots', str(slots)], 'jp_left (slots)')
    if tour:
        run(PY + ['tools/tour_text.py'], 'dialogue tour')
    rel = ROOT / 'release'
    rel.mkdir(exist_ok=True)
    patch = rel / PATCH
    run(PY + [str(SKILL / 'scripts' / 'bps.py'), 'make', str(ROM), str(built), str(patch)], 'bps make')
    check = ROOT / 'work' / 'reapplied.gba'
    run(PY + [str(SKILL / 'scripts' / 'bps.py'), 'apply', str(ROM), str(patch), str(check)], 'bps apply')
    if check.read_bytes() != built.read_bytes():
        sys.exit('re-applied patch differs from the build')
    o, b = ROM.read_bytes(), built.read_bytes()
    oc, om, os_ = hashes(o)
    bc, bm, bs = hashes(b)
    readme = (ROOT / 'docs' / 'README.release.txt').read_text(encoding='utf-8').format(
        version=VERSION, patch=PATCH, ocrc=oc, omd5=om, osha=os_, bcrc=bc, bmd5=bm, bsha=bs, size=len(o))
    (rel / 'README.txt').write_text(readme, encoding='utf-8', newline='\r\n')
    z = rel / ('%s_en.zip' % SLUG)
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(patch, PATCH)
        zf.write(rel / 'README.txt', 'README.txt')
    p = patch.read_bytes()
    print('release:', z)
    print('patch %s  crc32 %08X  sha1 %s' % (PATCH, zlib.crc32(p), hashlib.sha1(p).hexdigest()))
    print('patched ROM crc32 %s sha1 %s' % (bc, bs))
    return 0


if __name__ == '__main__':
    sys.exit(main())
