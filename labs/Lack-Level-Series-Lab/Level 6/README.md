# Level 6 — Walkthrough

> **Category:** Reverse Engineering (RE) / Fixed key + XOR decryption · **Difficulty:** Medium
> **Binary:** `level6.exe` · **Platform:** Windows x64
> **Goal:** Enter the correct **5-letter key** so the program prints `[+] Correct!`.

**TL;DR — the 5-letter key is `crack`.**

The key is checked character-by-character (`c`,`r`,`a`,`c`,`k`). Entering it prints:

```
[+] Correct! Decrypted flag: Pj``ffg"
```

⚠️ **Note:** the *decrypted flag* comes out as garbage (`Pj``ffg"`), **not** clean text. This is a **bug in the crackme** — the flag's XOR key is derived from the input's byte-sum, and `crack`'s sum doesn't match the value the blob was encrypted with. The author almost certainly intended the flag to read `Succeed!`. Details in §5. The actual objective — the accepted key — is unambiguously **`crack`**.

---

## 1. Recon

```bash
unzip -P crackmes.one "6a512a9e71ee08cad748dcba (1).zip"   # -> level6.exe
file level6.exe        # PE32+ console x86-64
```

Strings:

```
       CRACKME LEVEL 6
Enter 5-Letter Key:
[+] Correct! Decrypted flag:
[-] Access Denied. Decrypted output:  (Garbage!)
```

Single 5-letter input; pass/fail gate; both branches decrypt-and-print (the "(Garbage!)" label on the fail path is by now a familiar pattern — the decryption is independent of the pass/fail check).

---

## 2. Finding `main`

Anchor on `Enter 5-Letter Key:` → the reference sits in the function at `0x140001340` (pefile + capstone). The key is read into a `std::string` at `[rbp-0x30]`.

---

## 3. The logic — decrypt first, then gate

Reading `main` in order, three things happen:

### (a) Byte-sum of the input

The familiar auto-vectorized-plus-scalar loop sums the input's bytes into `edi`:

```asm
0x140001423  movsx eax, byte ptr [rcx]   ; sign-extend each byte
0x140001426  add   edi, eax
...                                        ; edi = sum of input bytes
0x140001430  xor   dil, 0x55             ; keybyte = (sum & 0xFF) XOR 0x55
```

### (b) Decrypt the blob with that key byte

```asm
0x140001460  movzx r9d, dil
0x140001464  xor   r9b, byte [rbx]       ; decrypted[i] = keybyte XOR blob[i]
```

The 7/8-byte blob is a runtime-initialized global at `0x140006218`; its initializer at `0x140001000` builds it from immediates:

```asm
mov dword ptr [rsp+0x30], 0x31313b01     ; 01 3b 31 31
mov dword ptr [rsp+0x34], 0x73363737     ; 37 37 36 73
```

Blob = `01 3b 31 31 37 37 36 73`.

### (c) The exact-character key check

Only *after* decrypting does the program validate the key, one byte at a time:

```asm
0x1400014a7  cmp r12, 5           ; length must be 5
0x1400014b9  cmp byte [key+0], 0x63   ; 'c'
0x1400014ca  cmp byte [key+4], 0x6b   ; 'k'
0x1400014dc  cmp byte [key+1], 0x72   ; 'r'
0x1400014ee  cmp byte [key+3], 0x63   ; 'c'
0x140001500  cmp byte [key+2], 0x61   ; 'a'
```

Reassembled in index order: `c r a c k` → **`crack`**. Any mismatch jumps to the "Access Denied" branch.

So the accepted key is fixed and unique: **`crack`**.

---

## 4. Verification

```bash
printf 'crack\n\n' | ./level6.exe
```

```
=============================
       CRACKME LEVEL 6
=============================

Enter 5-Letter Key:
[+] Correct! Decrypted flag: Pj``ffg"

Press Enter to exit...
```

`[+] Correct!` — the key is accepted. ✅

---

## 5. The decryption bug (why the "flag" is garbage)

The decryption key byte is `(sum_of_input_bytes & 0xFF) XOR 0x55`, **not** a fixed value tied to `crack`. For the correct key:

```
sum("crack") = 99+114+97+99+107 = 516 = 0x204   ->  0x204 & 0xFF = 0x04
keybyte      = 0x04 XOR 0x55 = 0x51
flag         = blob XOR 0x51 = "Pj``ffg"        <- garbage
```

Brute-forcing the blob against all 256 single-byte keys, the only near-clean plaintext is:

```
keybyte 0x52 -> "Sicceed!"   (i.e. the author's intended "Succeed!")
```

To hit key byte `0x52` you'd need an input whose byte-sum ≡ `0x52 XOR 0x55 = 0x07 (mod 256)` — but `crack` sums to `0x04`, and no 5-letter string can *both* satisfy the exact-character gate (`crack`) **and** have the byte-sum needed for a clean decode. The two mechanisms are decoupled: the byte-sum → key-byte path and the exact-character check were never reconciled by the author.

This is confirmed empirically against the binary — words whose byte-sum ends in `0x07` decrypt to the intended flag but fail the gate:

| Input | Sum | Key byte | Program output |
|-------|-----|----------|----------------|
| `crack` | 516 (0x204) | 0x51 | `[+] Correct! Decrypted flag: Pj``ffg"` (garbage) |
| `amber` / `angel` / `cobra` | 519 (0x207) | 0x52 | `[-] Access Denied. Decrypted output: Sicceed! (Garbage!)` |
| `bonus` / `crops` / `guess` | 551 (0x227) | 0x72 | `[-] Access Denied. Decrypted output: sICCEED (Garbage!)` |

**Conclusion:** the crackme's solution (the accepted 5-letter key) is `crack`. The "decrypted flag" it prints (`Pj``ffg"`) is a byproduct of a broken key-derivation and does not spell anything — the intended text was evidently `Succeed!` (the blob decrypts to `Sicceed!` under key `0x52`). No single input can produce both `[+] Correct!` and a meaningful flag; the level is bugged.

---

## Answer

| Field | Value |
|-------|-------|
| **5-letter key** | `crack` |
| **Program response** | `[+] Correct! Decrypted flag: Pj``ffg"` |
| **Intended flag (author bug)** | `Succeed!` (unreachable with the correct key) |
| **Decrypt key byte** | `(sum(input) & 0xFF) XOR 0x55` = `0x51` for `crack` |
| **Method** | Static disassembly (pefile + capstone); read the exact-character gate |

---

## Tools Used

| Tool | Purpose |
|------|---------|
| `unzip` / `file` | Extract & identify (PE32+ x64) |
| Python (`re`) | `strings` substitute |
| `pefile` | Section VAs, locate `main`, read blob pointer/initializer |
| `capstone` | Disassemble the byte-sum, XOR-decrypt, and character checks |
| Python | Brute the blob to show the intended-vs-actual flag mismatch |
| the binary | Dynamic confirmation of `[+] Correct!` |

---

## Takeaways / Methodology

1. **The pass/fail gate and the "flag" can be independent.** As in Levels 4–5, decryption runs on a key derived from user input *before* the validation check — but here they're not just independent, they're **inconsistent**, producing a garbage flag for the correct key.
2. **Read the exact-character comparisons in index order, not code order.** The compiler emitted the byte checks as `0,4,1,3,2`; sorting by offset gives `crack`. Don't transcribe them top-to-bottom.
3. **Trust the binary over your assumptions.** When `crack` produced garbage instead of clean text, the disciplined move was to *run it* and confirm the real output, then explain the discrepancy — rather than forcing a "nice" flag that the binary never actually emits.
4. **Recognize a designer bug and report it honestly.** The intended flag (`Succeed!`, key byte `0x52`) is one XOR value away from the actual (`0x51`), a classic off-by-one in the author's key math. The answer is still the accepted key `crack`; the flag text is simply broken.
