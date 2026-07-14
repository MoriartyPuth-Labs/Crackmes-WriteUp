#!/usr/bin/env python3
"""
Solver for CRACKME LEVEL 8 (level8.exe).

The password is validated by a tiny stack-based VM whose 54-byte bytecode
program is an embedded global. Opcodes (each instruction = 3 bytes:
opcode, operand, padding):

    op 1, idx :  r9 = password[idx]        (load a password char)
    op 2, k   :  r9 ^= k                   (xor with a constant)
    op 3, v   :  result &= (r9 == v)       (assert current r9 == v)

"[+] Correct!" requires result == 1 after running the whole program, and
the input length must be 6.

We recover the password by symbolic execution: track which index is
loaded and the accumulated XOR, and at each assert solve
    password[idx] = v XOR (accumulated_xor)

The flag is separately decrypted with key = ~(sum(password) & 0xFF).
NOTE: like Level 6, the correct password's sum does NOT match the key the
flag blob was encrypted with, so the displayed flag is garbage. The
intended flag ("Matrix!") is only recoverable by brute-forcing the blob.
"""
import struct

# ---- embedded 54-byte VM program (from the initializer immediates) ----
vals = [
 (0x40,'<I',0x2000001),(0x3c,'<I',0x7f030012),(0x38,'<I',0x10100),
 (0x34,'<I',0x3003402),(0x30,'<I',0x2010055),(0x2c,'<I',0x560200),
 (0x28,'<I',0x1002203),(0x24,'<I',0x78020003),(0x20,'<I',0xa0300),
 (0x1c,'<I',0x2000401),(0x18,'<I',0xf9030090),(0x14,'<I',0x50100),
 (0x10,'<I',0x300bc02),(0x0c,'<H',0xc4),
]
buf = bytearray(0x40)
for off, fmt, v in vals:
    p = struct.pack(fmt, v); pos = 0x40 - off; buf[pos:pos+len(p)] = p
prog = bytes(buf[0:0x36])

# ---- symbolic execution to solve the password ----
pw = {}
cur = None  # [index, xor_accum]
for i in range(0, len(prog), 3):
    op, operand = prog[i], prog[i+1]
    if op == 1:   cur = [operand, 0]
    elif op == 2: cur[1] ^= operand
    elif op == 3: pw[cur[0]] = operand ^ cur[1]
password = ''.join(chr(pw[i]) for i in range(6))
print("Password :", password)

# ---- flag blob + the (buggy) decryption ----
blob = struct.pack('<IHB', 0x0c0a1f33, 0x0617, 0x5f)
key_actual = (~sum(password.encode())) & 0xFF
print(f"Shown flag (key 0x{key_actual:02x}):", bytes(b ^ key_actual for b in blob))
# intended flag: brute the blob for printable text
for k in range(256):
    dec = bytes(b ^ k for b in blob)
    if dec.endswith(b'!') and all(32 <= c < 127 for c in dec):
        print(f"Intended flag (key 0x{k:02x}):", dec.decode())
