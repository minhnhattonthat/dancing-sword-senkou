"""Reach a scene from a cold boot and shoot it (no save, no playthrough).
  python -X utf8 tools/debug/warp.py SCENE [--rom build/dancing_sword_en.gba] [--out DIR] [--state-out S]
SCENE: a name from tools/debug/scenes.json, or block:N (pointer-table index 0-219: dialogue block N shown in the
bottom story box, then again in the top in-stage box), or all-blocks (every table index, one sheet per block).
Each run writes DIR/sheet.png (frames that changed)."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = Path(os.environ.get(
    'SKILL', 'C:/Users/Nathan/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game'))
EMU = SKILL / 'scripts' / 'emu.py'
sys.path.insert(0, str(ROOT / 'tools'))


def block_pages(rom, idx):
    from textlib import TABLE, read_block, u32
    d = Path(rom).read_bytes()
    return len(read_block(d, u32(d, TABLE + 4 * idx) - 0x08000000)[0])


def run(rom, out, route, frames, vars_, shot_every=None, shots=None, mash=None, state_out=None):
    cmd = [sys.executable, '-X', 'utf8', str(EMU), str(rom), '--out', str(out), '--route-str', route,
           '--frames', str(frames), '--script', str(ROOT / 'tools' / 'debug' / 'warp.lua'), '--sheet']
    for k, v in vars_.items():
        cmd += ['--var', '%s=%s' % (k, v)]
    if shot_every:
        cmd += ['--shot-every', str(shot_every)]
    if shots:
        cmd += ['--shots', shots]
    if mash:
        cmd += ['--mash', str(mash)]
    if state_out:
        cmd += ['--state-out', str(state_out)]
    return subprocess.call(cmd, cwd=ROOT)


BOOT = '700 -;6 start;120 -;6 start;120 -;6 a;120 -;6 a;'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('scene')
    ap.add_argument('--rom', default=str(ROOT / 'build' / 'dancing_sword_en.gba'))
    ap.add_argument('--out')
    ap.add_argument('--state-out')
    a = ap.parse_args()
    scenes = json.loads((ROOT / 'tools' / 'debug' / 'scenes.json').read_text(encoding='utf-8'))
    if a.scene == 'all-blocks':
        rc = 0
        for i in range(220):
            rc |= blocks(a, i)
        sys.exit(rc)
    if a.scene.startswith('block:'):
        sys.exit(blocks(a, int(a.scene[6:])))
    s = scenes[a.scene]
    out = Path(a.out or ROOT / 'work' / 'qa' / 'warp' / a.scene)
    sys.exit(run(a.rom, out, s['route'], s['frames'], s.get('vars', {}), s.get('shot_every'), s.get('shots'),
                 s.get('mash'), a.state_out))


def blocks(a, i):
    n = block_pages(a.rom, i)
    # warp.lua VIEW shoots each fully typed page (p001.png..) and presses A: bottom box, then the top box
    out = Path(a.out or ROOT / 'work' / 'qa' / 'warp' / ('block%03d' % i))
    rc = run(a.rom, out, BOOT + '30 -', 1500 + 2 * n * 450 + 1500, {'BLOCK': i, 'VIEW': 2 * n})
    subprocess.call([sys.executable, '-X', 'utf8', str(SKILL / 'scripts' / 'sheet.py'), str(out / 'p*.png'),
                     '--div', '1', '--cols', '2', '--max', '64', '--out', str(out / 'sheet.png')],
                    cwd=ROOT, stdout=subprocess.DEVNULL)
    return rc


if __name__ == '__main__':
    main()
