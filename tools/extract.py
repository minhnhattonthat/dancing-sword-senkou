"""Dump every dialogue page to script/NN.json. Never clobbers English: refuses if script/ exists unless --force,
and --force keeps en/status/notes of ids that still exist."""
import argparse
import sys

from textlib import ROM, SCRIPT, all_blocks, load_script, read_block, save_json, sjis, table_ptrs

PER_FILE = 100


def entries(d):
    ents, first = [], {}
    tbl = table_ptrs(d)
    for b in all_blocks(d):
        pages, _ = read_block(d, b)
        refs = [i for i, p in enumerate(tbl) if p == b]
        for n, (l1, l2, attr) in enumerate(pages):
            jp = [sjis(l1), sjis(l2)]
            e = {'id': '%06X.%02d' % (b, n), 'block': '%06X' % b, 'table_idx': refs, 'attr': attr.hex(),
                 'jp': jp, 'en': '', 'status': 'todo', 'notes': ''}
            key = tuple(jp)
            if any(jp) and key in first:
                e['same_as'] = first[key]
            elif any(jp):
                first[key] = e['id']
            else:
                e['status'] = 'empty'
            ents.append(e)
    return ents


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    d = open(ROM, 'rb').read()
    ents = entries(d)
    if SCRIPT.exists() and any(SCRIPT.glob('*.json')):
        if not a.force:
            sys.exit('script/ exists; use --force (keeps en/status/notes)')
        old = {e['id']: e for e in load_script()}
        for e in ents:
            if e['id'] in old:
                for k in ('en', 'status', 'notes'):
                    e[k] = old[e['id']][k]
        for f in SCRIPT.glob('*.json'):
            f.unlink()
    SCRIPT.mkdir(exist_ok=True)
    # split on block boundaries near PER_FILE pages
    files, cur = [], []
    for e in ents:
        if len(cur) >= PER_FILE and e['id'].endswith('.00'):
            files.append(cur)
            cur = []
        cur.append(e)
    files.append(cur)
    for i, f in enumerate(files):
        save_json(SCRIPT / ('%02d.json' % i), f)
    print('pages', len(ents), 'files', len(files), 'unique', sum(1 for e in ents if e['status'] == 'todo' and 'same_as' not in e))


if __name__ == '__main__':
    main()
