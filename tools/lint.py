"""Text lint over script/*.json. Prints errors + a count; exit 1 on any error.
Checks: encodable, every wrapped line <= LINE_PX and < 42 bytes, no Japanese left in en, done entries have en,
glossary terms (glossary.md table: JP | English | Avoid), stub last line, ordinal suffix after a digit variable."""
import re
import sys

import font_en
from textlib import LINE, LINE_PX, ROOT, load_script, paginate, wrap

JP = re.compile('[぀-ヿ一-鿿＀-￯]')


def glossary():
    rows = []
    p = ROOT / 'glossary.md'
    if not p.exists():
        return rows
    for line in p.read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 2 and JP.search(cells[0]) and cells[1] and not cells[0].startswith('-'):
            rows.append((cells[0], cells[1], [a.strip() for a in cells[2].split(',')] if len(cells) > 2 and cells[2] else []))
    return rows


def lint(ents, strict_todo=False):
    errs, warns = [], 0
    gl = glossary()
    for e in ents:
        en = e['en']
        if e['status'] == 'empty' or e.get('same_as') and not en:
            continue
        if not en:
            if strict_todo:
                errs.append('%s: no English' % e['id'])
            continue
        bad = [c for c in en if c != '\n' and not font_en.encodable(c)]
        if bad:
            errs.append('%s: unencodable %r' % (e['id'], ''.join(sorted(set(bad)))))
            continue
        if JP.search(en):
            errs.append('%s: Japanese left' % e['id'])
        for l in wrap(en):
            if font_en.text_width(l) > LINE_PX:
                errs.append('%s: word wider than the box: %r' % (e['id'], l))
            if len(l) >= LINE:
                errs.append('%s: line over %d bytes: %r' % (e['id'], LINE - 1, l))
        pages = paginate(en)
        if len(pages) > 1 and pages[-1][1] == '' and len(pages[-1][0]) < 6:
            errs.append('%s: stub last page %r' % (e['id'], pages[-1][0]))
        if re.search(r'\d(st|nd|rd|th)\b', en) and re.search(r'1th|2th|3th|11st|12nd|13rd', en):
            errs.append('%s: ordinal suffix' % e['id'])
        jp = ''.join(e['jp'])
        for j, eng, avoid in gl:
            if j in jp and eng.lower() not in en.lower():
                warns += 1
            for a in avoid:
                if a and re.search(r'\b%s\b' % re.escape(a), en):
                    errs.append('%s: avoid %r (use %r)' % (e['id'], a, eng))
    return errs, warns


def main():
    strict = '--strict' in sys.argv
    ents = load_script()
    errs, warns = lint(ents, strict)
    for x in errs[:200]:
        print(x)
    todo = sum(1 for e in ents if e['status'] not in ('empty',) and not e.get('same_as') and not e['en'])
    print('lint: %d errors, %d glossary warnings, %d untranslated' % (len(errs), warns, todo))
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
