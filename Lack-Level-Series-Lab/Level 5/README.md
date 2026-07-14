# Level 5 — Walkthrough

> **Category:** Reverse Engineering (RE) / Two-part license key + XOR decryption · **Difficulty:** Medium
> **Binary:** `level5.exe` · **Platform:** Windows x64
> **Goal:** Enter **Key Part 1** and **Key Part 2** (both numeric) so the program prints
> `[+] LICENSE VALIDATED!` followed by `[+] Flag: <flag>`.

**TL;DR**

- **Part 1 = `1700`**, **Part 2 = `5565`** → `[+] Flag: Victory!`
- Constraint: `Part1 % 17 == 0` and `Part2 == (Part1 XOR 0x1337) + 0x2A`
- Flag decryption key = `Part2 & 0xFF`; only `0xBD` yields a readable flag (`Victory!`) from the embedded 8-byte blob.

---

## 1. Recon

```bash
unzip -P crackmes.one 6a512a7b71ee08cad748dcb6.zip   # -> level5.exe
file level5.exe        # PE32+ console x86-64
```

Strings (full picture this time — pay attention to *all* four outcome branches, not just the obvious ones):

```
       CRACKME LEVEL 5
Enter Key Part 1:
Enter Key Part 2:
[+] LICENSE VALIDATED!
[+] Flag:
[-] INVALID LICENSE KEY!
[-] Decrypted output:  (Garbage!)
```

Two numeric inputs, a pass/fail gate ("LICENSE VALIDATED" vs "INVALID"), and — notably — **the failure path still decrypts and prints something**, just labeled "(Garbage!)". That's a strong hint the decryption key is derived from the input regardless of whether the license check passes, exactly like Level 4's independent "Success vs readable" split.

*(Lesson learned mid-analysis: an early narrower grep missed the "INVALID"/"Garbage" strings entirely and led to a wrong first guess. Always dump the full string list before modeling the branches — see Takeaways.)*

---

## 2. Locating `main` and the storage order

Anchor on `Enter Key Part 1:` / `Enter Key Part 2:` → `main` at `0x140001230` (pefile + capstone).

Reading the code in strict execution order:

```asm
; print "Enter Key Part 1: "
0x14000126b  lea rdx, [Part1_prompt]
...
; std::cin >> Part1   -> stored at [rbp-0x34]
0x14000127e  lea rdx, [rbp - 0x34]
0x140001289  call <istream::operator>>>

; print "Enter Key Part 2: "
0x1400012c0  lea rdx, [Part2_prompt]
...
; std::cin >> Part2   -> stored at [rbp-0x38]
0x1400012cc  lea rdx, [rbp - 0x38]
0x1400012d7  call <istream::operator>>>
```

**Important:** the two locals are *not* in the order you'd guess from the code layout — `Part1` ends up at `[rbp-0x34]` and `Part2` at `[rbp-0x38]`. Getting this backwards was my first mistake (see Takeaways) and produced "INVALID LICENSE KEY!" with a garbage decrypt on the first attempt.

---

## 3. The validation + decryption logic

```asm
0x14000130e  mov edi, dword ptr [rbp-0x38]   ; edi = Part2
...
0x14000138a  mov r8d, dword ptr [rbp-0x34]   ; r8d = Part1
0x140001391  test r8d, r8d
0x140001393  mov  eax, 0xf0f0f0f1            ; magic constant for /17
0x140001398  mul  r8d
0x14000139b  shr  edx, 4                     ; edx = Part1 / 17
0x14000139e  imul ecx, edx, 0x11             ; ecx = (Part1/17) * 17
0x1400013a1  cmp  r8d, ecx
0x1400013a4  jne  invalid                    ; fails unless Part1 % 17 == 0

0x1400013a6  xor  r8d, 0x1337                ; r8d = Part1 XOR 0x1337
0x1400013ad  add  r8d, 0x2a                  ;      + 0x2A
0x1400013b1  cmp  edi, r8d                   ; Part2 == that value?
0x1400013b4  jne  invalid
                                              ; else: LICENSE VALIDATED
```

`0xf0f0f0f1` followed by `shr edx,4` is the classic MSVC "divide by 17" reciprocal-multiplication trick — recognizing it saves you from misreading it as an arbitrary multiply.

**Constraints:**

```
Part1 % 17 == 0
Part2       == (Part1 XOR 0x1337) + 0x2A
```

Regardless of whether the check passes, the flag is decrypted using `Part2`'s low byte:

```asm
0x140001340  movzx r9d, dil        ; dil = Part2 & 0xFF  (note: edi = Part2, set earlier)
0x140001344  xor   r9b, byte [rbx] ; decrypted[i] = key XOR blob[i]
```

So `key = Part2 & 0xFF`, applied to an 8-byte blob regardless of pass/fail — matching the "(Garbage!)" failure-path string seen earlier.

### Extracting the blob

The pointer at `0x1400051e0` sits past `.data`'s raw size (runtime-initialized). Its initializer at `0x140001000`:

```asm
mov dword ptr [rsp+0x30], 0xc9ded4eb
mov dword ptr [rsp+0x34], 0x9cc4cfd2
```

Little-endian bytes: **`eb d4 de c9 d2 cf c4 9c`**.

---

## 4. Solving

Two unknowns (`Part1`, `Part2`) are linked by one equation, plus `Part1 % 17 == 0`. Brute-forcing `Part1` over multiples of 17 and testing which produces a printable decrypted blob:

```python
blob = bytes([0xeb,0xd4,0xde,0xc9,0xd2,0xcf,0xc4,0x9c])
for part1 in range(0, 200000, 17):
    part2 = (part1 ^ 0x1337) + 0x2A
    key = part2 & 0xFF
    dec = bytes(b ^ key for b in blob)
    if dec == b"Victory!":
        print(part1, part2)
```

```
1700 5565
```

**Part 1 = 1700, Part 2 = 5565 → flag `Victory!`**

---

## 5. Verification

```bash
printf '1700\n5565\n\n' | ./level5.exe
```

```
=============================
       CRACKME LEVEL 5
=============================

Enter Key Part 1: Enter Key Part 2:
[+] LICENSE VALIDATED!
[+] Flag: Victory!

Press Enter to exit...
```

Confirmed.

---

## Answer

| Field | Value |
|-------|-------|
| **Flag** | `Victory!` |
| **Part 1** | `1700` |
| **Part 2** | `5565` |
| **Constraints** | `Part1 % 17 == 0`, `Part2 == (Part1 XOR 0x1337) + 0x2A` |
| **Flag key** | `Part2 & 0xFF` = `0xBD` |
| **Method** | Static disassembly (pefile + capstone), solve two linked constraints, brute the mod-17 free variable |

---

## Tools Used

| Tool | Purpose |
|------|---------|
| `unzip` / `file` | Extract & identify (PE32+ x64) |
| Python (`re`) | `strings` substitute |
| `pefile` | Section VAs, locate `main`, read blob pointer |
| `capstone` | Disassemble the validation + XOR-decrypt logic |
| Python | Solve the constraint system by brute-forcing the mod-17 variable |
| `keygen.py` | Generate the (Part1, Part2) pair and preview the flag |
| the binary | Dynamic confirmation |

---

## Takeaways / Methodology

1. **Grep for outcome strings broadly, not just the happy path.** My first string dump filtered too aggressively and missed `INVALID LICENSE KEY!` / `Garbage!` entirely, leading to a wrong mental model (I assumed there was no fail branch). Always list *every* printable string once, unfiltered, before deciding what's relevant.
2. **Local variable order ≠ source order.** `std::cin >> Part1` printed first, but the compiler placed `Part1`'s storage *after* `Part2`'s on the stack (`rbp-0x34` vs `rbp-0x38`). Track each `lea`/`call operator>>` pair explicitly instead of assuming top-to-bottom = first-to-second.
3. **Recognize the reciprocal-multiplication division idiom.** `mov eax, 0xf0f0f0f1; mul r8d; shr edx,4` is `r8d / 17` — MSVC's standard trick for compile-time-constant integer division. Spotting it immediately reveals a modulus/divisibility check.
4. **A failure path that still prints "(Garbage!)" is a tell** that the decryption key is derived unconditionally from user input, independent of the validation gate — same pattern as Level 4, now made explicit in the UI text itself.
5. **Two linked unknowns + one small modulus = brute the free variable.** Rather than solving algebraically, iterating `Part1` over multiples of 17 and checking the decrypted output directly is faster and less error-prone.
