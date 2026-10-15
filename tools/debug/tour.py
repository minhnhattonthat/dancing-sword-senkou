"""Run the screen-survey routes in tools/debug/scenes.json sequentially (one Mesen at a time).
  python -X utf8 tools/debug/tour.py [--rom ROM] [--only name,name] [--out work/qa/tour]"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rom', default=str(ROOT / 'build' / 'dancing_sword_en.gba'))
    ap.add_argument('--only')
    ap.add_argument('--out', default=str(ROOT / 'work' / 'qa' / 'tour'))
    a = ap.parse_args()
    scenes = json.loads((ROOT / 'tools' / 'debug' / 'scenes.json').read_text(encoding='utf-8'))
    names = a.only.split(',') if a.only else list(scenes)
    rc = 0
    for n in names:
        r = subprocess.call([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'debug' / 'warp.py'), n,
                             '--rom', a.rom, '--out', str(Path(a.out) / n)], cwd=ROOT,
                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(n, 'exit', r, flush=True)
        rc |= r
    sys.exit(rc)


if __name__ == '__main__':
    main()
