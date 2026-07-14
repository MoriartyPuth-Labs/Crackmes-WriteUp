# Level 9 — Walkthrough

> **Category:** Reverse Engineering (RE) / 32-bit arithmetic constraint · **Difficulty:** Hard
> **Binary:** `level9.exe` · **Platform:** Windows x64
> **Goal:** Enter the correct **8-character password** to print `[+] Correct!`.

**TL;DR — the password is `lrys'ume`** (bytes `6c 72 79 73 27 75 6d 65`).

The 8 input bytes are treated as two 32-bit integers and fed through a mixing function that must hit two hardcoded constants. The system is fully determined, so it's solved algebraically — no brute force. As in Levels 6 & 8, the printed flag is garbage (`{JXX…`); the intended flag was `Pass!!!!`.

---

## 1. Recon

```bash
unzip -P crackmes.one 6a512b0ba6d88566c06d765f.zip   # -> level9.exe
file level9.exe        # PE32+ console x86-64
```

Strings: `Enter 8-Letter Password:`, `[+] Correct! Decrypted flag:`, `[-] Access Denied. Decrypted output:  (Garbage!)` — same shell as Levels 6/8, new validation.

---

## 2. Finding the check

Anchor on `Enter 8-Letter Password:` → `main` at `0x140001360` (pefile + capstone). After the (now-standard) sum-keyed flag decryption, the real check begins at `0x1400014a7`:

```asm
0x1400014a7  cmp r12, 8              ; length must be 8
0x1400014ab  jne denied
0x1400014b9  mov ecx, dword [pw]     ; A = password[0..3]  (LE int)
0x1400014c3  mov edx, dword [pw+4]   ; B = password[4..7]  (LE int)
0x1400014c6  lea eax, [rdx+rcx]      ; S = A + B
0x1400014c9  xor edx, eax            ; D = B XOR S
0x1400014cb  lea ecx, [rdx+0x1337]   ; D + 0x1337
0x1400014d1  xor ecx, eax            ; ecx = (D + 0x1337) XOR S
0x1400014d3  cmp ecx, 0x656d4278     ; must equal C1
0x1400014d9  jne denied
0x1400014db  lea eax, [rdx+rcx]      ; eax = D + ecx
0x1400014de  cmp eax, 0x22f8d52c     ; must equal C2
0x1400014e3  jne denied
                                     ; else: Correct!
```

So with `S = A+B`, `D = B XOR S`, and constants `C1 = 0x656d4278`, `C2 = 0x22f8d52c`:

```
ecx = (D + 0x1337) XOR S   ==   C1
eax = D + ecx              ==   C2
```

---

## 3. Solving algebraically

The second equation collapses the whole thing. Since `ecx` must equal `C1`:

```
eax = D + ecx = D + C1 = C2     =>   D = C2 - C1        (mod 2**32)
```

`D` is now known. Back-substitute into the first equation:

```
S = (D + 0x1337) XOR C1
```

And from the definitions:

```
B = D XOR S
A = S - B                       (mod 2**32)
```

Every value is uniquely determined — there is exactly one `(A, B)`:

```python
M  = 1 << 32
C1 = 0x656d4278; C2 = 0x22f8d52c
D  = (C2 - C1) % M
S  = ((D + 0x1337) % M) ^ C1
B  = D ^ S
A  = (S - B) % M
password = struct.pack('<II', A, B)   # A=0x7379726c, B=0x656d7527
```

`A = 0x7379726c` → LE bytes `6c 72 79 73` = `lrys`
`B = 0x656d7527` → LE bytes `27 75 6d 65` = `'ume`

**Password = `lrys'ume`.** (Not a dictionary word — it's just whatever byte pattern the two integer targets decode to.)

---

## 4. Verification

```bash
printf "lrys'ume\n" | ./level9.exe
```

```
       CRACKME LEVEL 9
Enter 8-Letter Password:
[+] Correct! Decrypted flag: {JXX
```

`[+] Correct!` — accepted. ✅ (The "flag" is garbage; see next.)

---

## 5. The garbage flag (same bug as Levels 6 & 8)

Flag blob = `bc 8d 9f 9f cd cd cd cd`; decrypt key = `~(sum(password) & 0xFF)`:

```
sum("lrys'ume") = 824 = 0x338  ->  0x338 & 0xFF = 0x38
keybyte         = ~0x38 = 0xc7
flag            = blob XOR 0xc7 = "{JXX\n\n\n\n"     <- garbage
```

Brute-forcing the blob:

```
key 0xec -> "Pass!!!!"     (the intended flag)
```

(The four trailing `!` come from the four identical `0xcd` bytes.) Key `0xec` needs `sum & 0xFF == ~0xec = 0x13`, but the unique password sums to `0x38`. Because the arithmetic constraint pins `(A, B)` — hence every byte, hence the sum — no accepted password can produce key `0xec`. The validator and the flag-key derivation are decoupled, exactly as in Levels 6 and 8.

**Conclusion:** password is `lrys'ume` (verified `[+] Correct!`); intended flag `Pass!!!!`, unreachable through the correct password due to the recurring key-derivation bug.

---

## Answer

| Field | Value |
|-------|-------|
| **Password** | `lrys'ume` (`6c 72 79 73 27 75 6d 65`) |
| **Validation** | two LE dwords `A,B`; `(( (B^(A+B)) +0x1337)^(A+B))==0x656d4278` and `(B^(A+B))+0x656d4278==0x22f8d52c` |
| **Intended flag** | `Pass!!!!` (key `0xec`) |
| **Shown flag (bug)** | `{JXX…` (key `0xc7` from `~(sum & 0xFF)`) |
| **Method** | Static disassembly (pefile + capstone), solve the constraint system by algebra |

---

## Tools Used

| Tool | Purpose |
|------|---------|
| `unzip` / `file` | Extract & identify (PE32+ x64) |
| Python (`re`) | `strings` substitute |
| `pefile` | Section VAs, locate `main`, read flag blob initializer |
| `capstone` | Disassemble the integer-mixing check |
| Python | Solve the two equations for `A`, `B` (no brute force) |
| the binary | Dynamic confirmation of `[+] Correct!` |

---

## Takeaways / Methodology

1. **Bytes-as-integers is a common obfuscation.** `mov ecx, [pw]` / `mov edx, [pw+4]` packs 8 chars into two dwords; the "password check" is then just arithmetic on those two numbers. Recognize the packing and work in integer space.
2. **Look for the collapsing equation.** `eax = D + ecx` with both `ecx` and `eax` pinned to constants immediately gives `D = C2 - C1` — no search needed. Always check whether a later constraint linearizes an earlier one.
3. **A fully-determined system has a unique key.** Two 32-bit equations fixed both dwords exactly; there's nothing to brute. Solve, don't guess.
4. **The flag bug recurs a third time.** Same pattern as Levels 6 and 8: the password is pinned, but the flag key comes from `~(sum & 0xFF)` which doesn't match the blob. Report the real password and note the intended flag (`Pass!!!!`) rather than claiming clean output the binary never prints.
