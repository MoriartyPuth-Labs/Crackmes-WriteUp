#!/usr/bin/env python3
"""
Keygen for CRACKME LEVEL 4 (level4.exe).

Recovered by static analysis:

  1. sum   = sum of the username's bytes
  2. valid serial S = sum * 0x7B         (0x7B = 123)   -> grants "Success"
  3. the program then decrypts a 7-byte flag blob with a single-byte key:
         key = (entered_serial & 0xFF) XOR 0x34
         flag = blob XOR key
     blob = 34 08 0b 11 02 03 46
     The REAL flag "Solved!" only appears when key == 0x67, i.e. when
         (S & 0xFF) == 0x53   <=>   sum % 256 == 9
     Any other username still prints "Success" but shows a garbage flag.

So a *fully correct* solution (Success + readable "Solved!") needs a
username whose byte-sum is congruent to 9 mod 256.
"""
import sys

BLOB = bytes([0x34, 0x08, 0x0b, 0x11, 0x02, 0x03, 0x46])

def solve(username: str):
    s = sum(username.encode())
    serial = s * 0x7B
    key = (serial & 0xFF) ^ 0x34
    flag = bytes(b ^ key for b in BLOB)
    readable = (s % 256 == 9)
    return serial, flag, readable

def suggest_username(sumtarget_mod=9):
    """Return a short printable username whose byte-sum % 256 == 9."""
    total = sumtarget_mod + 256          # smallest reachable with printable ascii
    # three chars: two 'd' (100) + remainder
    a = b = 100
    c = total - a - b
    while c < 32:
        a -= 1; c = total - a - b
    return chr(a) + chr(b) + chr(c)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user = sys.argv[1]
    else:
        user = suggest_username()
        print(f"[*] No username given; using generated one with sum % 256 == 9")
    serial, flag, readable = solve(user)
    print(f"Username : {user}")
    print(f"Serial   : {serial}")
    print(f"Decrypts to: {flag.decode(errors='replace')}"
          + ("" if readable else "   (garbage - sum % 256 != 9)"))
