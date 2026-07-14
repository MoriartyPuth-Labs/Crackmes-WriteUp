#!/usr/bin/env python3
"""
Solver for CRACKME LEVEL 10 (BOSS) - level10.exe.

The password is validated by a base-31 polynomial hash (Java String.hashCode):

    h = 0
    for c in password:           # c is a *signed* char
        h = (h * 31 + c) mod 2**32
    # "[+] Correct!" requires  h == 0x3D17141A

The hash is computed inside a worker thread (via _beginthreadex) and the
result stored in a global; the threading/mutex machinery is just window
dressing around this one loop.

Because it's a hash, MANY strings collide onto the target. We recover one
printable, whitespace-free preimage via meet-in-the-middle (3 + 3 chars).
Whitespace must be excluded because `std::cin >> string` stops at spaces.

The flag is XOR-decrypted with key = (h & 0xFF) XOR 0xAA, using the STORED
hash. Since a correct password makes h == 0x3D17141A (low byte 0x1A),
key = 0x1A ^ 0xAA = 0xB0, which cleanly decrypts the blob to "Perfect!".
Unlike Levels 6/8/9, this level is NOT bugged - the winning password
produces the real flag.
"""
import struct
from itertools import product

M = 1 << 32
TARGET = 0x3D17141A

# ---- flag ----
blob = struct.pack('<II', 0xd6c2d5e0, 0x91c4d3d5)
key = (TARGET & 0xFF) ^ 0xAA
print("Flag:", bytes(b ^ key for b in blob).decode())

# ---- invert the base-31 hash (meet-in-the-middle, 3 + 3 printable chars) ----
B3 = pow(31, 3, M)
invB3 = pow(B3, -1, M)
def h3(t):
    h = 0
    for c in t:
        h = (h * 31 + c) % M
    return h

rng = range(0x21, 0x7f)          # printable, no whitespace (cin >> stops at spaces)
prefixes = {}
for a, b, c in product(rng, rng, rng):
    prefixes.setdefault(h3((a, b, c)), (a, b, c))

password = None
for a, b, c in product(rng, rng, rng):
    need = ((TARGET - h3((a, b, c))) % M) * invB3 % M
    if need in prefixes:
        password = bytes(prefixes[need] + (a, b, c))
        break

# verify
h = 0
for ch in password:
    h = (h * 31 + ch) % M
assert h == TARGET
print("Password (one valid preimage):", password.decode())
print("hashCode check: 0x%08x == 0x%08x" % (h, TARGET))
