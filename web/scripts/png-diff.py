#!/usr/bin/env python3
"""
web/scripts/png-diff.py

Compare two pairs of PNGs at the byte level after decoding + unfiltering.
Returns IDENTICAL when the two PNGs decode to the same pixel stream, or
"diff bytes X/Y (Z.ZZZ%)" otherwise.

Usage:
  python3 web/scripts/png-diff.py \\
    a1.png a2.png b1.png b2.png

Two comparisons are run; the first two args are compared first, the
third and fourth args are compared second. (Designed to compare 1440
and 393 pairs in one invocation.)
"""

import struct
import sys
import zlib


def parse_png(path):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'not png: {path}'
    chunks = {}
    i = 8
    while i < len(data):
        ln = struct.unpack('>I', data[i:i + 4])[0]
        typ = data[i + 4:i + 8].decode('ascii')
        body = data[i + 8:i + 8 + ln]
        chunks.setdefault(typ, []).append(body)
        i += 12 + ln
        if typ == 'IEND':
            break
    ihdr = chunks['IHDR'][0]
    w, h, depth, color = struct.unpack('>IIBB', ihdr[:10])
    return w, h, depth, color, b''.join(chunks['IDAT'])


def unfilter(w, h, depth, color, raw):
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    bpp = max(1, channels * (depth // 8))
    stride = w * bpp
    out = bytearray()
    prev = bytes(stride)
    pos = 0
    for _y in range(h):
        ftype = raw[pos]
        pos += 1
        line = bytearray(raw[pos:pos + stride])
        pos += stride
        if ftype == 0:
            pass
        elif ftype == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 0xFF
        elif ftype == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 0xFF
        elif ftype == 3:
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + (left + prev[x]) // 2) & 0xFF
        elif ftype == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                if pa <= pb and pa <= pc:
                    pred = a
                elif pb <= pc:
                    pred = b
                else:
                    pred = c
                line[x] = (line[x] + pred) & 0xFF
        else:
            raise ValueError('bad filter')
        out.extend(line)
        prev = bytes(line)
    return bytes(out)


def diff_pixels(p, q):
    w1, h1, d1, c1, raw1 = parse_png(p)
    w2, h2, d2, c2, raw2 = parse_png(q)
    if (w1, h1, d1, c1) != (w2, h2, d2, c2):
        return f'DIFF meta: {w1}x{h1} d{d1} c{c1} vs {w2}x{h2} d{d2} c{c2}'
    raw1 = zlib.decompress(raw1)
    raw2 = zlib.decompress(raw2)
    px1 = unfilter(w1, h1, d1, c1, raw1)
    px2 = unfilter(w1, h1, d1, c1, raw2)
    if px1 == px2:
        return 'IDENTICAL'
    n = min(len(px1), len(px2))
    diff = sum(1 for i in range(n) if px1[i] != px2[i])
    return f'diff bytes {diff}/{n} ({100 * diff / n:.3f}%)'


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('usage: png-diff.py a1.png a2.png b1.png b2.png', file=sys.stderr)
        sys.exit(1)
    print(f'{sys.argv[1]} vs {sys.argv[2]}: {diff_pixels(sys.argv[1], sys.argv[2])}')
    print(f'{sys.argv[3]} vs {sys.argv[4]}: {diff_pixels(sys.argv[3], sys.argv[4])}')