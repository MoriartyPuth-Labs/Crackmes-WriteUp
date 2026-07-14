# Ultimate Boss Level — Final — Walkthrough

> **Category:** Reverse Engineering (RE) / Anti-debug + jump-table VM + multi-part license · **Difficulty:** Ultimate Boss
> **Binary:** `UltimateBoss.exe` · **Platform:** Windows x64
> **Goal:** Enter a **Username** + **Part 1** + **Part 2** to print `[+] Access Granted!` and the clean message `Wow you did it!`.

**TL;DR**

- **Username:** any non-empty string; **Part 1** = `sum(username_bytes) × 31`; **Part 2** = `(Part1 ^ 0x1337) + 0x7B`.
- For the *clean* message, pick a username whose `Part2 & 0xFF == 0x78`. Example: **`ZZB` / `7626` / `3960`** → `[+] Message: Wow you did it!`
- Everything is static — the anti-debug (IsDebuggerPresent, timing) only matters under a debugger; solving offline sidesteps it entirely.

---

## 1. Recon

```bash
unzip -P crackmes.one 6a5158ee71ee08cad748dcc9.zip   # -> UltimateBoss.exe
file UltimateBoss.exe        # PE32+ console x86-64, 30 KB
```

The string dump shows **no UI text** (all prompts are runtime-decrypted) and an anti-RE import set:

```
IsDebuggerPresent   CheckRemoteDebuggerPresent   GetThreadContext
GetTickCount64      GetProcAddress               Sleep
```

Running it normally reveals the flow:

```
THE ULTIMATE LICENSE CHECK
Enter Username: … Enter Part 1: … Enter Part 2: …
```

Three inputs: a username string and two integers.

---

## 2. The validation is a jump-table VM

`main` calls a validator at `0x140001d50`. Its args (from the call site at `0x140002753`) are `rcx = username`, `edx = [rsp+0x48] = Part 1`, `r8d = [rsp+0x44] = Part 2`. The function is a **state-machine VM**:

```asm
0x140001d5b  lea r14, [rip-0x1d62]          ; r14 = image base 0x140000000
0x140001d62  xor ebp, 0x1337                ; ebp = Part1 ^ 0x1337
0x140001d70  add ebp, 0x7b                  ;      + 0x7B   (expected Part2)
0x140001d7b  mov r15d, 0x63                 ; 0x63 = terminal "fail" state
dispatch:
0x140001d81  movsxd rax, r10d               ; state
0x140001d84  movzx eax, byte [r14+rax+0x1ec0]   ; opcode = state_table[state]
0x140001d8d  mov ecx, dword [r14+rax*4+0x1ea4]  ; handler = jump_table[opcode]
0x140001d95  add rcx, r14
0x140001d98  jmp rcx
```

Extracting the two tables (`0x140001ea4` = jump table, `0x140001ec0` = state table):

| State | Opcode | Handler | Check |
|-------|--------|---------|-------|
| 0 | 0 | `0x1d9a` | username length ≠ 0 (else → 99) |
| 1 | 1 | `0x1dab` | `Part1 == sum(username) × 31` (else → 99) |
| 3 | 3 | `0x1e83` | `Part2 == (Part1 ^ 0x1337) + 0x7B` (else → 99) |
| 4 | 4 | `0x1e94` | set result = 1 → **success** |
| 99 | 5 | `0x1e96` | return result (0) → **fail** |

The byte-sum handler is the by-now-familiar SSE + scalar `movsx`/`add` loop, then `imul eax, r9d, 0x1f` (×31). So the license is:

```
Part1 = sum(username_bytes) * 31          (signed char sum, mod 2**32)
Part2 = (Part1 XOR 0x1337) + 0x7B         (mod 2**32)
```

---

## 3. Anti-debug (and why it doesn't matter offline)

The validator call is bracketed by `GetTickCount64`:

```asm
0x14000273c  call GetTickCount64           ; start
0x140002753  call 0x140001d50              ; validate
0x14000275c  call GetTickCount64           ; end
0x140002762  sub rax, rbx
0x140002765  cmp rax, 0x1f4                ; 500 ms
0x14000276b  jbe 0x140002862              ; normal (fast) -> real path
             ; (slow path -> decrypts "[!] Debugger Detected!")
```

If the check takes **> 500 ms** (i.e. someone is single-stepping), control goes to a branch that prints a decoy `[!] Debugger Detected!` (blob A, XOR `0x4f`) and sleeps. There are also `IsDebuggerPresent` / `CheckRemoteDebuggerPresent` / `GetThreadContext` (debug-register) probes resolved via `GetProcAddress`. **Static analysis defeats all of it for free** — we never run under a debugger, and we compute the answer offline.

---

## 4. The message decryption (the real prize)

On success the program prints two fixed strings and then the real message:

```asm
; blob B  -> "\n[+] Access Granted!\n"      (XOR 0x4f, fixed)
; blob@0x140009218 -> "[+] Message: "        (XOR 0x4f, fixed)
0x140002862  movzx r14d, byte [rsp+0x44]     ; Part2 low byte
0x140002868  xor   r14b, 0x3e               ; message key = (Part2 & 0xFF) XOR 0x3E
             ; decrypt blob C (15 bytes) with that key, print it
```

Blob C (from its initializer at `0x140001560`) = `11 29 31 66 3f 29 33 66 22 2f 22 66 2f 32 67`. Brute-forcing the single-byte key:

```
msg key 0x46 -> "Wow you did it!"      (needs Part2 & 0xFF == 0x78)
```

So the intended message decodes cleanly **only when `Part2 & 0xFF == 0x78`**.

### Why this one is solvable (unlike Levels 6/8/9)

In Levels 6/8/9 the password was pinned exactly, so its byte-sum — and thus the flag key — was fixed and wrong. **Here the username is free.** `Part2` is a function of the username's byte-sum, so we simply choose a username whose derived `Part2` ends in `0x78`. Both conditions (Access Granted *and* clean message) are satisfiable at once. The finale gets the design right.

---

## 5. Solving

Find the smallest byte-sum `S` with `Part2 & 0xFF == 0x78`, then build any printable username summing to `S`:

```python
M = 1<<32
def parts(S):
    p1 = (S*31) % M
    p2 = ((p1 ^ 0x1337) + 0x7B) % M
    return p1, p2
S = next(s for s in range(1, 10000) if parts(s)[1] & 0xFF == 0x78)   # S = 246
# username summing to 246, e.g. "ZZB" (90+90+66)
p1, p2 = parts(246)   # 7626, 3960
```

- **Username = `ZZB`** (byte-sum 246)
- **Part 1 = `7626`**
- **Part 2 = `3960`** (low byte `0x78`)

Any username whose byte-sum ≡ 246 (mod ~ the period that keeps `Part2 & 0xFF == 0x78`) works — `ZZB` is just the smallest.

---

## 6. Verification

```bash
printf 'ZZB\n7626\n3960\n' | ./UltimateBoss.exe
```

```
THE ULTIMATE LICENSE CHECK
Enter Username: Enter Part 1: Enter Part 2:
[+] Access Granted!
[+] Message: Wow you did it!
```

Confirmed — grant **and** clean message. ✅

(For comparison, `test` / `13888` / `9714` also gets `[+] Access Granted!` but prints a garbage message, because `test`'s Part2 low byte isn't `0x78`.)

---

## Answer

| Field | Value |
|-------|-------|
| **Username** | `ZZB` (any non-empty name with `Part2 & 0xFF == 0x78`) |
| **Part 1** | `7626` = `sum("ZZB") × 31` |
| **Part 2** | `3960` = `(Part1 ^ 0x1337) + 0x7B` |
| **Message** | `Wow you did it!` |
| **Message key** | `(Part2 & 0xFF) XOR 0x3E` = `0x46` |
| **Method** | Static disassembly (pefile + capstone), decode the VM tables, solve the license, choose username for a clean message |

---

## Tools Used

| Tool | Purpose |
|------|---------|
| `unzip` / `file` | Extract & identify (PE32+ x64) |
| Python (`re`) | Confirm strings are runtime-encrypted; flag the anti-debug imports |
| `pefile` | Section VAs, locate `main` + validator, read the VM tables and message blobs |
| `capstone` | Disassemble the jump-table VM, timing guard, and blob decryptors |
| Python | Extract the state/jump tables; brute the message key; solve for a username |
| the binary | Dynamic confirmation (runs fine without a debugger) |

---

## Takeaways / Methodology

1. **Anti-debug is a static-analysis problem.** IsDebuggerPresent, DR-register checks via `GetThreadContext`, and `GetTickCount64` timing all target *dynamic* analysis. Reading the code and computing the answer offline neutralizes every one of them — never attach a debugger to a binary built to detect them.
2. **A jump-table dispatcher is a VM.** `movzx opcode, [base+state]` → `mov off, [base+opcode*4]` → `add; jmp` is the signature. Dump both tables from the file, map opcode→handler, and the "obfuscated" control flow becomes a plain ordered checklist.
3. **Recover the license algebra, then keygen it.** `Part1 = sum×31`, `Part2 = (Part1 ^ 0x1337) + 0x7B` — two lines once the VM is decoded. The username's freedom makes it a keygen, not a fixed answer.
4. **A free input fixes the recurring flag bug.** The message key is `(Part2 & 0xFF) ^ 0x3E`, derived from user-controlled data. Because the username (hence Part2) is ours to choose, we can hit the exact key that decrypts `Wow you did it!` — the correct way to wire a "decrypt-on-success" message, and a deliberate contrast with Levels 6/8/9.
5. **Distinguish decoy output from real output.** `[!] Debugger Detected!` and garbage messages are dead ends; the disassembly shows which branch is the genuine success path (fast timing + valid + `Part2` low byte `0x78`).
