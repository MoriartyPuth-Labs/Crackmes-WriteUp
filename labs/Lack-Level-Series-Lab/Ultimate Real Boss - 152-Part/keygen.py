#!/usr/bin/env python3
"""
Keygen for THE ULTIMATE 152-Part LICENSE CHECK (UltimateRealBoss.exe).

Inputs: Username (string) + 152 integer Parts.

Validation runs in a jump-table state-machine VM (function 0x140001d50),
wrapped in the same GetTickCount64 (<=500 ms) + IsDebuggerPresent /
CheckRemoteDebuggerPresent / GetThreadContext anti-debug as the previous
boss. The VM checks:

    state0: username non-empty AND the Parts vector has exactly 152 ints
    state2: Part[0] == sum(username_bytes) * 31            (signed, mod 2^32)
    loop (states 4/5, index i = 1..151):
            Part[i] == ((i + 0x1337) XOR Part[i-1]) + i*123 (mod 2^32)
    state6: success

So every Part after the first is a chained function of the previous one,
seeded by the username's byte-sum.

On success the program decrypts a 15-byte message blob with
    key = (Part[151] & 0xFF) XOR 0x3E
The intended message "Wow you did it!" needs key 0x46, i.e.
Part[151] & 0xFF == 0x78. The username is FREE, so we search byte-sums
until the whole 152-long chain lands the last part's low byte on 0x78 -
giving Access Granted AND the clean message together.

Usage: python keygen.py [username]   (prints the 152-line input)
"""
import sys

M = 1 << 32
BLOB = bytes.fromhex('112931663f293366222f22662f3267')

def s32(x):
    x &= M - 1
    return x - M if x >= (1 << 31) else x

def chain(S):
    p = [(S * 31) % M]
    for i in range(1, 152):
        p.append(((( i + 0x1337) ^ p[i-1]) + i * 123) % M)
    return p

def username_for_sum(S):
    """Shortest printable, whitespace-free username with byte-sum S."""
    chars = []
    while S > 0:
        c = min(S, 0x7e)
        if c < 0x21:                     # avoid space/control (cin >> stops at ws)
            chars[-1] = chr(ord(chars[-1]) - (0x21 - c)); c = 0x21
        chars.append(chr(c)); S -= c
    return ''.join(chars)

if len(sys.argv) > 1:
    user = sys.argv[1]
else:
    # pick the smallest byte-sum whose chain gives a clean message
    S = next(s for s in range(1, 100000) if chain(s)[151] & 0xFF == 0x78)
    user = username_for_sum(S)

S = sum(user.encode())
parts = chain(S)
key = (parts[151] & 0xFF) ^ 0x3E
msg = bytes(b ^ key for b in BLOB).decode('latin1')

sys.stderr.write(f"Username : {user!r}  (byte-sum {S})\n")
sys.stderr.write(f"Part[151] & 0xFF = 0x{parts[151] & 0xFF:02x}  ->  Message: {msg}\n")
sys.stderr.write("License input (username + 152 parts) on stdout:\n")

print(user)
for p in parts:
    print(s32(p))
