"""One-command check: pytest + text lint. Exit non-zero on any failure."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
r1 = subprocess.call([sys.executable, '-X', 'utf8', '-m', 'pytest', '-q', str(ROOT / 'tests')], cwd=ROOT)
r2 = subprocess.call([sys.executable, '-X', 'utf8', str(ROOT / 'tools' / 'lint.py')] + sys.argv[1:], cwd=ROOT)
sys.exit(1 if r1 or r2 else 0)
