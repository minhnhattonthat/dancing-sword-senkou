"""Dry-run the dialogue wrap: python -X utf8 tools/fit.py "English text" -> pages, lines, pixel widths (max 160)."""
import sys

import font_en
from textlib import LINE_PX, paginate

for n, page in enumerate(paginate(' '.join(sys.argv[1:]).replace('\\n', '\n')), 1):
    for l in page:
        print('p%d %3dpx%s | %s' % (n, font_en.text_width(l), ' OVER' if font_en.text_width(l) > LINE_PX else '', l))
