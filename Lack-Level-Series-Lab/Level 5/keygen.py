#!/usr/bin/env python3
"""
Keygen for CRACKME LEVEL 5 (level5.exe).

Recovered by static analysis:

    Part 1 (int) must be a multiple of 17           (Part1 % 17 == 0)
    Part 2 (int) must equal  (Part1 XOR 0x1337) + 0x2A

If both hold, the program prints "[+] LICENSE VALIDATED!" and decrypts an
8-byte flag blob with a single-byte XOR key = Part2 & 0xFF:

    blob = eb d4 de c9 d2 cf c4 9c
    flag = blob XOR (Part2 & 0xFF)

The only key that yields a printable flag is Part2 & 0xFF == 0xBD, which
decrypts to "Victory!". Any (Part1, Part2) pair satisfying the two
equations above reproduces the same Part2 & 0xFF (it's fully determined
by Part1 mod 256), so in practice Part1 = 1700, Part2 = 5565 is the
canonical minimal solution.
"""
import sys

BLOB = bytes([0xeb, 0xd4, 0xde, 0xc9, 0xd2, 0xcf, 0xc4, 0x9c])

def derive(part1: int):
    part2 = (part1 ^ 0x1337) + 0x2A
    key = part2 & 0xFF
    flag = bytes(b ^ key for b in BLOB)
    valid = (part1 % 17 == 0)
    return part2, key, flag, valid

def find_minimal():
    for part1 in range(0, 1_000_000, 17):
        part2, key, flag, valid = derive(part1)
        if valid and flag == b"Victory!":
            return part1, part2, flag

if __name__ == "__main__":
    if len(sys.argv) > 1:
        part1 = int(sys.argv[1])
        part2, key, flag, valid = derive(part1)
        if not valid:
            print(f"Part1={part1} is not a multiple of 17 - LICENSE will be INVALID.")
    else:
        part1, part2, flag = find_minimal()
    part2, key, flag, valid = derive(part1)
    print(f"Part 1 : {part1}")
    print(f"Part 2 : {part2}")
    print(f"Flag   : {flag.decode(errors='replace')}")
