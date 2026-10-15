"""Translation batches.
  split            -> work/tl/bNN.tsv (+ build/terms_bNN.txt) for every unique untranslated page, in script order
  check bNN        -> validate work/tl/bNN.out.tsv (ids, encodable ASCII, widths, glossary Avoid); prints OK
  merge bNN        -> check, then write the English into script/*.json (status 'done')
  pairs bNN        -> work/tl/bNN.pairs.txt for the reviewer (JP/EN with +-2 context)
Input TSV: id<TAB>speaker<TAB>form<TAB>limit<TAB>jp (' / ' joins the two JP lines)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
from lint import JP, glossary  # noqa: E402
from textlib import LINE, LINE_PX, ROOT, SCRIPT, load_script, save_json, wrap  # noqa: E402

TL = ROOT / 'work' / 'tl'
PER_BATCH = 135
SPEAKERS = ['Kyoko', 'Claire', 'Rinrei', 'Mimi', 'Luciel']


def speaker(attr):
    p = int(attr[:2], 16)
    if p == 0x64:
        return 'none (narration / off-screen / NPC)'
    if p == 0xFF:
        return 'none'
    if p < 0x14:
        return SPEAKERS[p // 4]
    return 'other (portrait %02X: enemy/NPC, identify from context)' % p


def units(ents):
    return [e for e in ents if e['status'] != 'empty' and not e.get('same_as')]


def split():
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / 'build').mkdir(exist_ok=True)
    us = [e for e in units(load_script()) if not e['en']]
    gl = glossary()
    chunks, cur = [], []
    for e in us:  # cut only at block boundaries so a scene is never split
        if len(cur) >= PER_BATCH and e['block'] != cur[-1]['block']:
            chunks.append(cur)
            cur = []
        cur.append(e)
    chunks.append(cur)
    for n, chunk in enumerate(chunks):
        b = 'b%02d' % n
        rows = ['%s\t%s\tdlg\t~60ch/page\t%s' % (e['id'], speaker(e['attr']), ' / '.join(x for x in e['jp'] if x))
                for e in chunk]
        (TL / (b + '.tsv')).write_text('\n'.join(rows) + '\n', encoding='utf-8', newline='\n')
        jp = ''.join(''.join(e['jp']) for e in chunk)
        terms = ['%s | %s' % (j, e) for j, e, _ in gl if j in jp]
        (ROOT / 'build' / ('terms_%s.txt' % b)).write_text('\n'.join(terms) + '\n', encoding='utf-8', newline='\n')
        print(b, len(chunk), 'entries', len(jp), 'jp chars')


def read_out(b):
    p = TL / (b + '.out.tsv')
    out = {}
    for ln in p.read_text(encoding='utf-8-sig').splitlines():
        if not ln.strip():
            continue
        if '\t' not in ln:
            raise SystemExit('%s: line without tab: %r' % (b, ln[:60]))
        k, v = ln.split('\t', 1)
        if k in out:
            raise SystemExit('%s: duplicate id %s' % (b, k))
        out[k] = v.replace('\\n', '\n')
    return out


def check(b, quiet=False):
    ids = [ln.split('\t', 1)[0] for ln in (TL / (b + '.tsv')).read_text(encoding='utf-8').splitlines() if ln]
    out = read_out(b)
    errs = []
    if set(out) != set(ids):
        errs.append('id set differs: missing %s extra %s' % (sorted(set(ids) - set(out))[:5], sorted(set(out) - set(ids))[:5]))
    gl = glossary()
    jpby = {e['id']: ''.join(e['jp']) for e in load_script()}
    for k, v in out.items():
        bad = sorted(set(c for c in v if c != '\n' and not font_en.encodable(c)))
        if bad or '\t' in v or '\\u' in v or JP.search(v):
            errs.append('%s: bad chars %r' % (k, ''.join(bad)))
            continue
        if not v.strip():
            errs.append('%s: empty' % k)
        for l in wrap(v):
            if font_en.text_width(l) > LINE_PX or len(l) >= LINE:
                errs.append('%s: unbreakable run too wide: %r' % (k, l))
        if re.search(r'\b(1th|2th|3th)\b', v):
            errs.append('%s: ordinal' % k)
        for j, e, avoid in gl:
            for a in avoid:
                if a and re.search(r'\b%s\b' % re.escape(a), v):
                    errs.append('%s: avoid %r, use %r' % (k, a, e))
            if j in jpby.get(k, '') and e.lower() not in v.lower() and not quiet:
                pass  # glossary presence is a lint warning, not a batch error (word forms vary)
    for x in errs:
        print(x)
    if not errs:
        print('OK', b, len(out), 'entries')
    return not errs


def merge(b):
    if not check(b, quiet=True):
        raise SystemExit('merge refused')
    out = read_out(b)
    for f in sorted(SCRIPT.glob('*.json')):
        import json
        ents = json.loads(f.read_text(encoding='utf-8'))
        ch = False
        for e in ents:
            if e['id'] in out:
                e['en'] = out[e['id']]
                e['status'] = 'done'
                ch = True
        if ch:
            save_json(f, ents)
    print('merged', b, len(out))


def pairs(b):
    ents = load_script()
    ids = set(read_out(b))
    idx = {e['id']: i for i, e in enumerate(ents)}
    lines = []
    for e in ents:
        if e['id'] not in ids:
            continue
        i = idx[e['id']]
        ctx = [x for x in ents[max(0, i - 2):i] if x['block'] == e['block']]
        for c in ctx:
            lines.append('   %s | %s / %s' % (c['id'], ' / '.join(c['jp']), c['en'] or '(same as %s)' % c.get('same_as')))
        lines.append('>> %s | [%s] %s' % (e['id'], speaker(e['attr']), ' / '.join(x for x in e['jp'] if x)))
        lines.append('   EN: %s' % e['en'].replace('\n', '\\n'))
    p = TL / (b + '.pairs.txt')
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print(p)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'split':
        split()
    elif cmd == 'check':
        sys.exit(0 if check(sys.argv[2]) else 1)
    elif cmd == 'merge':
        merge(sys.argv[2])
    elif cmd == 'pairs':
        pairs(sys.argv[2])
