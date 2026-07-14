# `Level` Crackme Series — Complete Walkthroughs (12 Challenges)

A full set of solutions for the **Level** crackme series by author **Lack** — **10 numbered levels plus two boss finales** (12 total), all Windows x64 PE32+ console programs. Each asks for input and prints a success/flag or an "Access Denied" message. (The binaries' embedded PDB path shows the build username `knze2` / project `crackmetest` — that's the build machine, not the author handle.)

Every challenge folder contains a `README.md` (rich) and `writeup.txt` (plain text) with full reasoning, disassembly, tools, and takeaways. Challenges that need code ship a `keygen.py` / `solve.py`.

## Method (applies to every challenge)

Static-first, **no debugger required** — which also neutralizes the bosses' anti-debug for free. The repeatable recipe:

1. `unzip -P crackmes.one <id>.zip` → `file` to confirm PE32+ x64.
2. Dump strings (Python `re` stand-in for `strings`) to model the branches — **all** of them, not just the happy path.
3. Locate `main` by anchoring on a known UI string and scanning `.text` for the RIP-relative `lea` that references it (`pefile` + `capstone`).
4. Read the check; recover the algorithm; solve it (decode / keygen / algebra / symbolic exec / hash inversion / VM decode).
5. Verify against the binary.

## Results at a glance

| # | Challenge | New primitive introduced | Answer | Flag / Message |
|---|-----------|--------------------------|--------|----------------|
| 1 | [Level 1](Level%201) | Plaintext string in `.rdata` | `password` | — |
| 2 | [Level 2](Level%202) | XOR 0x5A vs stack blob | `reverse` | — |
| 3 | [Level 3](Level%203) | Keygen: `sum×1337 ^ 0x5A5A` | `admin` / `719707` | — |
| 4 | [Level 4](Level%204) | Keygen + serial-keyed XOR flag | `admin` / `64083` | `Solved!` |
| 5 | [Level 5](Level%205) | Two-part license + XOR flag | `1700` / `5565` | `Victory!` |
| 6 | [Level 6](Level%206) | Exact-char key + XOR flag *(bugged flag)* | `crack` | `Succeed!` (intended; unreachable) |
| 7 | [Level 7](Level%207) | XOR-0x5A password + decoy menu UI | `license` | `Welcome to the Secret Menu!` |
| 8 | [Level 8](Level%208) | Bytecode VM (load/xor/assert) *(bugged flag)* | `matrix` | `Matrix!` (intended; unreachable) |
| 9 | [Level 9](Level%209) | Bytes-as-two-int32 arithmetic constraint *(bugged flag)* | `lrys'ume` | `Pass!!!!` (intended; unreachable) |
| 10 | [Level 10](Level%2010) | Base-31 hash in a worker thread (BOSS) | `!St3r{` (any preimage) | `Perfect!` |
| Boss | [Ultimate Boss - Final](Ultimate%20Boss%20-%20Final) | Anti-debug + jump-table VM, 2-part license | `ZZB` / `7626` / `3960` | `Wow you did it!` |
| Final | [Ultimate Real Boss - 152-Part](Ultimate%20Real%20Boss%20-%20152-Part) | Anti-debug + VM, **152-part chained keygen** | `)` + 152 parts | `Wow you did it!` |

## Difficulty arc

Plaintext → XOR-obfuscated → keygen → serial-as-crypto-key → multi-part constraints → decoy UI → **bytecode VM** → **integer-arithmetic constraint** → **threaded hash inversion** → **anti-debug + jump-table VM** → **152-part chained keygen**.

Each challenge introduces *exactly one* new primitive on top of the last, so you never face two unknowns at once. By the time the VMs and anti-debug appear, the author's idioms (the SSE+scalar signed byte-sum, the `imul` keygens, runtime-built `std::string` blobs) are already familiar — the new layer is the only thing to study. It teaches the RE *method* — `file` → strings → anchor on a UI string → read the check → invert it — as much as any individual trick.

## The recurring "flag bug" (Levels 6, 8, 9)

Levels 4 onward decrypt a flag with a key derived from the input's byte-sum (`~(sum & 0xFF)` or similar), *independent* of the pass/fail check. In **Levels 6, 8, and 9** the author never reconciled the two: the one accepted answer's byte-sum yields the **wrong** XOR key, so the correct input prints a garbage flag. The intended flags (`Succeed!`, `Matrix!`, `Pass!!!!`) only appear on the *rejected* path, for other inputs whose sum happens to match — proven per-level in each writeup.

The other challenges wire it correctly, which shows the author knew the right pattern:
- **Levels 4, 5, 7, 10** — the check value *is* (or determines) the key, so the winning input yields the real flag.
- **Both bosses** — the message key hangs off user-controlled data (`Part2` low byte / the tail of a username-seeded chain), and because the username is **free**, you choose one that steers the key to the clean value (`0x78`) — grant *and* clean message together.

## Verdict

A strong teaching set — roughly **8/10 as a curriculum, ~6.5 as a pure challenge**. Standout: the disciplined, incremental design that mirrors real RE workflow, with genuinely varied techniques (a bytecode interpreter, integer-packing algebra, a Java-style hashCode inverted by meet-in-the-middle, threading-as-misdirection, `IsDebuggerPresent`/DR/timing anti-debug, a jump-table state machine). Marked down for the three-level flag bug and for the hardest-*looking* finales being more theatrical than deep (the 152-part boss collapses to one free variable; the threading and anti-debug are walked past statically). For its clear target — learning to go from `strings` to Ghidra-free scripted disassembly — it's one of the better on-ramps around, and worth finishing end to end.

## Tooling

`unzip`, `file`, Python (`re`, `struct`, `itertools`), `pefile`, `capstone`, and the binaries themselves for dynamic confirmation. **No Ghidra/IDA needed** — a scripted capstone pass plus reasoning about `.rdata`/`.data` layout (and dumping the VMs' jump/state tables) was sufficient throughout. The bosses' anti-debug (`IsDebuggerPresent`, `CheckRemoteDebuggerPresent`, `GetThreadContext` DR checks, `GetTickCount64` timing) never triggers because everything is solved offline.

## Layout

```
Lack-Level-Series-Lab/
├── README.md                          (this file)
├── Level 1/ … Level 10/
│   ├── README.md                      rich walkthrough
│   ├── writeup.txt                    plain-text walkthrough
│   └── keygen.py | solve.py           (levels 3, 4, 5, 8, 9, 10)
├── Ultimate Boss - Final/             (2-part license, anti-debug + VM)
│   ├── README.md · writeup.txt · solve.py
└── Ultimate Real Boss - 152-Part/     (152-part chained keygen)
    ├── README.md · writeup.txt · keygen.py
```

## Quick reference — running the solvers

```bash
# keygen/solve scripts print the answer(s); pipe the multi-input ones straight in
python "Level 3/keygen.py" admin
python "Ultimate Boss - Final/solve.py"
python "Ultimate Real Boss - 152-Part/keygen.py" | ./UltimateRealBoss.exe
```
