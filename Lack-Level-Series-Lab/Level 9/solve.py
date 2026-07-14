#!/usr/bin/env python3
"""
Solver for CRACKME LEVEL 9 (level9.exe).

The 8-byte password is read as two little-endian 32-bit integers:
    A = dword at password[0..3]
    B = dword at password[4..7]

The validator computes (all mod 2**32):
    S   = A + B
    D   = B XOR S
    ecx = ((D + 0x1337) XOR S)         ; must == 0x656d4278   (C1)
    eax = (D + ecx)                    ; must == 0x22f8d52c   (C2)

Solve directly:
    eax = D + C1 = C2   =>   D = C2 - C1
    S   = (D + 0x1337) XOR C1
    B   = D XOR S
    A   = S - B
The password is the little-endian bytes of A followed by B (unique).

The flag is separately XOR-decrypted with key = ~(sum(password) & 0xFF).
As in Levels 6 and 8, the correct password's sum does NOT match the key
the flag blob was encrypted with, so the shown flag is garbage; the
intended flag ("Pass!!!!") is only recoverable by brute-forcing the blob.
"""
import struct

M = 1 << 32
C1 = 0x656d4278
C2 = 0x22f8d52c

D = (C2 - C1) % M
S = ((D + 0x1337) % M) ^ C1
B = D ^ S
A = (S - B) % M
password = struct.pack('<II', A, B)
print("Password :", password.decode('latin1'), " (hex", password.hex() + ")")

# verify the exact arithmetic
s = (A + B) % M
d = B ^ s
ecx = ((d + 0x1337) % M) ^ s
eax = (d + ecx) % M
assert ecx == C1 and eax == C2, "constraint mismatch"

# flag blob + (buggy) decryption
blob = struct.pack('<II', 0x9f9f8dbc, 0xcdcdcdcd)
shown_key = (~sum(password)) & 0xFF
print(f"Shown flag (key 0x{shown_key:02x}):", bytes(b ^ shown_key for b in blob))
for k in range(256):
    dec = bytes(b ^ k for b in blob)
    if dec.startswith(b'Pass') and all(32 <= c < 127 for c in dec):
        print(f"Intended flag (key 0x{k:02x}):", dec.decode())
