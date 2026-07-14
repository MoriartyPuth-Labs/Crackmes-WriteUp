#!/usr/bin/env python3
"""
Solver for THE ULTIMATE LICENSE CHECK (UltimateBoss.exe) - series finale.

Three inputs: Username (string), Part 1 (int), Part 2 (int).

Validation runs inside a jump-table state-machine VM (function 0x140001d50),
wrapped in a GetTickCount64 timing guard (must finish <= 500 ms) plus
IsDebuggerPresent / CheckRemoteDebuggerPresent / GetThreadContext anti-debug.
The VM states check, in order:
    state0: username non-empty
    state1: Part1 == sum(username_bytes) * 31        (signed char sum, mod 2^32)
    state3: Part2 == (Part1 XOR 0x1337) + 0x7B       (mod 2^32)
    state4: success

On success the program prints two fixed strings (XOR 0x4f):
    "\n[+] Access Granted!\n"  and  "[+] Message: "
then the real message = blobC XOR ((Part2 & 0xFF) XOR 0x3E).
The intended message "Wow you did it!" needs message key 0x46, i.e.
Part2 & 0xFF == 0x78.

Unlike Levels 6/8/9, the USERNAME is free, so we can choose one whose
derived Part2 ends in 0x78 -> Access Granted AND the clean message together.
(Blob A, "[!] Debugger Detected!", is shown only if the timing guard trips.)
"""
import struct

M = 1 << 32

def parts(S):
    p1 = (S * 31) % M
    p2 = ((p1 ^ 0x1337) + 0x7B) % M
    return p1, p2

def make_username(S):
    """A printable username whose byte-sum is exactly S."""
    chars = []
    while S > 0:
        c = min(S, 90)                       # 'Z'
        if c < 32:                           # borrow from previous char
            chars[-1] = chr(ord(chars[-1]) - (32 - c)); c = 32
        chars.append(chr(c)); S -= c
    return ''.join(chars)

# smallest byte-sum whose Part2 low byte == 0x78 (message key 0x46 -> clean text)
S = next(s for s in range(1, 100000) if parts(s)[1] & 0xFF == 0x78)
user = make_username(S)
p1, p2 = parts(S)
assert sum(user.encode()) == S

# decode the message blob to prove the flag
blobC = struct.pack('<IIHB', 0x66312911, 0x6633293f, 0x322f, 0x67)  # note: rebuilt below
# rebuild blobC exactly as laid out in memory (15 bytes)
blobC = struct.pack('<II', 0x66312911, 0x6633293f) + struct.pack('<I', 0x66222f22) \
        + struct.pack('<H', 0x322f) + struct.pack('<B', 0x67)
msg_key = (p2 & 0xFF) ^ 0x3E
message = bytes(b ^ msg_key for b in blobC).decode()

print(f"Username : {user}   (byte-sum {S})")
print(f"Part 1   : {p1}")
print(f"Part 2   : {p2}   (low byte 0x{p2 & 0xFF:02x})")
print(f"Message  : {message}")
