"""Graphics-text edits (docs/re/graphics.md). apply(rom, orig) writes every translated graphic into rom;
ranges() lists the ROM byte ranges it may write (for the romdiff test)."""

EDITS = []   # (offset, bytes) filled in as graphics are translated


def apply(rom, orig):
    for off, data in EDITS:
        rom[off:off + len(data)] = data


def ranges():
    return [(o, o + len(d)) for o, d in EDITS]
