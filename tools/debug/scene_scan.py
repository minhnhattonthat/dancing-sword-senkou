"""Jump the scene machine to every scene id (0x0300199A, table 0x0879AC64) from the title screen and shoot each,
to find screens no route reaches (game over, continue, ...). python -X utf8 tools/debug/scene_scan.py [--rom R] [--ids 0-29]"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EMU = Path(r'H:\translation\batch\.claude\skills\translate-retro-game\scripts\emu.py')

ap = argparse.ArgumentParser()
ap.add_argument('--rom', default=str(ROOT / 'build' / 'dancing_sword_en.gba'))
ap.add_argument('--ids', default='0-29')
a = ap.parse_args()
lo, hi = map(int, a.ids.split('-'))
for i in range(lo, hi + 1):
    out = ROOT / 'work' / 'qa' / 'scenes' / ('s%02d' % i)
    r = subprocess.call([sys.executable, '-X', 'utf8', str(EMU), a.rom, '--out', str(out), '--route-str',
                         '700 -;6 start;300 -', '--frames', '2400', '--mash', '200', '--shot-every', '100',
                         '--script', str(ROOT / 'tools' / 'debug' / 'warp.lua'), '--var', 'SCENE_ID=%d' % i,
                         '--var', 'SCENE_AT=1000', '--var', 'CHAR=0', '--timeout', '120'],
                        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print('scene', i, 'exit', r, flush=True)
