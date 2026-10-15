"""Assemble asm/*.s (Thumb) with keystone. Symbols (NAME -> int) are substituted as whole words before assembling."""
import re
from pathlib import Path

import keystone

ROOT = Path(__file__).resolve().parent.parent


def assemble(name, base, symbols=None):
    src = (ROOT / 'asm' / name).read_text(encoding='utf-8')
    src = '\n'.join(l.split('@', 1)[0] for l in src.splitlines())
    for k, v in (symbols or {}).items():
        src = re.sub(r'\b%s\b' % k, '0x%X' % v, src)
    src = src.replace('.thumb', '')
    ks = keystone.Ks(keystone.KS_ARCH_ARM, keystone.KS_MODE_THUMB)
    enc, _ = ks.asm(src, base)
    return bytes(enc)


def thumb_ldr_bx(addr, target, reg=1):
    """`ldr rN,[pc,#k]; bx rN; (pad); .word target|1` at addr (a 2-byte aligned Thumb address)."""
    lit = (addr + 4 + 3) & ~3 if (addr + 4) & 3 else addr + 4
    k = lit - ((addr + 4) & ~3)
    out = bytes([k >> 2, 0x48 | reg]) + bytes([reg << 3, 0x47])
    out += b'\x00\x00' * ((lit - addr - 4) // 2)
    return out + (target | 1).to_bytes(4, 'little')
