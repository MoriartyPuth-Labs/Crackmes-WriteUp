#!/usr/bin/env python3
"""
Keygen for CRACKME LEVEL 3 (level3.exe).

Algorithm (recovered by static analysis):
    serial = (sum_of_username_bytes * 0x539) XOR 0x5A5A
             where 0x539 = 1337, 0x5A5A = 23130

The serial is read as a signed 32-bit int and compared directly, so any
username whose computed value stays in int range produces a valid key.
"""
import sys

def keygen(username: str) -> int:
    s = sum(username.encode())      # printable ASCII < 128 => signed == unsigned
    return (s * 0x539) ^ 0x5A5A

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else input("Username: ")
    print(f"Username: {user}")
    print(f"Serial  : {keygen(user)}")
