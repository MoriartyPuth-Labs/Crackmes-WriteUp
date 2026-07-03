<div align="center">

# 🖥️ MalwareTech VM1
### Virtual Machine Reverse Engineering & Static Analysis

<img src="https://github.com/user-attachments/assets/19167dcc-61d3-4a5d-b8f2-b58f9ccb4c04" width="860" alt="MalwareTech VM1 Banner"/>

<br/>

![Platform](https://img.shields.io/badge/MalwareTech_Labs-000000?style=for-the-badge&logo=windows&logoColor=white)
![Type](https://img.shields.io/badge/Static_Analysis-8A2BE2?style=for-the-badge&logo=databricks&logoColor=white)
![Arch](https://img.shields.io/badge/x86__64-0071C5?style=for-the-badge&logo=intel&logoColor=white)
![OS](https://img.shields.io/badge/Windows_64--bit-0078D4?style=for-the-badge&logo=windows11&logoColor=white)
![Difficulty](https://img.shields.io/badge/Difficulty-Medium-F5A623?style=for-the-badge)
![Solver](https://img.shields.io/badge/Solver-Python_3-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flag](https://img.shields.io/badge/Flag-Captured_🏆-2EA44F?style=for-the-badge)

</div>

---

<div align="center">

### `507 bytes` · `Custom 8-bit VM` · `XOR Decryption` · `No Execution Required`

</div>

---

## 📌 About

A 507-byte binary (`ram.bin`) hides a flag inside a hand-rolled **custom 8-bit Virtual Machine**. The challenge: reverse the VM's architecture, reconstruct its instruction set, and decrypt the flag using **pure static analysis** — the binary never touches a CPU.

| | |
|---|---|
| 🖥️ **Lab** | MalwareTech VM1 |
| 🔬 **Type** | Static Analysis — Custom VM Reversing |
| ⚙️ **Architecture** | x86_64 |
| 🪟 **Platform** | Windows 64-bit |
| ⚡ **Difficulty** | Medium |
| 📦 **Download** | [vm1.rar](https://labs.malwaretech.com/files/virtualization/vm1.rar) |
| 🔑 **Archive Password** | `MalwareTechLabs` |
| 🎯 **Target File** | `ram.bin` (507 bytes) |
| 🏆 **Flag** | `FLAG{VIRTUAL-MACHINE-UNDERSTANDING}` |

---

## 🗺️ Analysis Pipeline

```
 ┌──────────┐    ┌─────────────┐    ┌──────────────────┐
 │ ram.bin  │───▶│  Hex Dump   │───▶│  Memory Layout   │
 │ (507 B)  │    │  Analysis   │    │  Mapping         │
 └──────────┘    └─────────────┘    └────────┬─────────┘
                                             │
                                             ▼
 ┌──────────────┐    ┌─────────────────┐    ┌────────────────┐
 │  FLAG 🏆     │◀───│ Python Emulator │◀───│ ISA            │
 │  Decrypted   │    │  solver.py      │    │ Reconstruction │
 └──────────────┘    └─────────────────┘    └────────────────┘
```

---

## 🔬 Technical Analysis

### 1️⃣ Memory Layout

The raw hex dump immediately revealed a clean boundary separating data from executable bytecode.

<img src="https://github.com/user-attachments/assets/ead45377-ead3-40bc-a98a-cd497ec982f3" width="800" alt="Hex dump memory layout"/>

<br/>

| Region | Offset | Size | Contents |
|---|---|---|---|
| 📦 **Data Section** | `0x00` → `0xFE` | 255 bytes | Encrypted flag data + VM state |
| ⚙️ **Bytecode Section** | `0xFF` → `0x1FB` | 252 bytes | VM instructions (IP starts here) |

> 💡 The Instruction Pointer always initialises at `0xFF`. Every instruction is exactly **3 bytes wide** — no variable-length encoding.

---

### 2️⃣ Instruction Set Architecture

The VM runs a textbook **Fetch → Decode → Execute** loop over 3-byte fixed-width instructions:

```
 Byte 0          Byte 1          Byte 2
┌───────────────┬───────────────┬───────────────┐
│    OPCODE     │   OPERAND 1   │   OPERAND 2   │
│    1 byte     │    1 byte     │    1 byte     │
└───────────────┴───────────────┴───────────────┘
```

Full ISA recovered through manual bytecode tracing:

| Opcode | Mnemonic | Pseudocode | Description |
|---|---|---|---|
| `0x01` | **SET** | `RAM[op1] = op2` | Write immediate value into RAM |
| `0x02` | **LOAD** | `REG = RAM[op1]` | Load RAM value into register |
| `0x03` | **XOR** | `RAM[op1] ^= REG` | XOR RAM address with register |
| _other_ | **HALT** | `break` | Terminate execution |

---

### 3️⃣ Fetch-Decode-Execute Loop

The engine advances 3 bytes per cycle, reading from the bytecode section:

```python
counter = 0

while running:
    #  ── FETCH ──────────────────────────────────
    opcode = bytecode[counter + 0xFF]   # instruction
    op1    = bytecode[counter + 0x100]  # operand 1
    op2    = bytecode[counter + 0x101]  # operand 2

    counter += 3                         # advance IP

    #  ── DECODE & EXECUTE ────────────────────────
    decode_and_execute(opcode, op1, op2)
```

---

### 4️⃣ Static Emulator — `solver.py`

No execution. No sandboxing. No dynamic analysis. A Python emulator processes `ram.bin` cold:

```python
# ──────────────────────────────────────────────
#  MalwareTech VM1 — Static Emulator
#  solver.py
# ──────────────────────────────────────────────

ram            = bytearray(open("ram.bin", "rb").read())
register       = 0
counter        = 0
BYTECODE_START = 0xFF

while True:
    ip = BYTECODE_START + counter

    # Bounds check — stop if past end of file
    if ip + 2 >= len(ram):
        break

    opcode, op1, op2 = ram[ip], ram[ip + 1], ram[ip + 2]
    counter += 3

    # ── Execute ──────────────────────────────────
    if   opcode == 0x01:   ram[op1]  = op2          # SET
    elif opcode == 0x02:   register  = ram[op1]      # LOAD
    elif opcode == 0x03:   ram[op1] ^= register      # XOR
    else:                  break                      # HALT

# ── Extract decrypted flag from data section ──
flag = bytes(ram[0x00:0xFF]).split(b"\x00")[0].decode()
print(f"[+] Flag: {flag}")
```

**What the script does, step by step:**

1. 📂 Load `ram.bin` into a mutable byte array
2. 📍 Begin execution at offset `0xFF`
3. 🔁 Emulate `SET` → `LOAD` → `XOR` cycles
4. 🔑 XOR keys are pulled from within the data section itself
5. 🏁 When a `HALT` opcode is hit, the flag sits decrypted in `RAM[0x00:0xFF]`

---

## 🏆 Flag

<div align="center">

```
╔══════════════════════════════════════════════════╗
║                                                  ║
║    FLAG{VIRTUAL-MACHINE-UNDERSTANDING}           ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

</div>

---

## 🧰 Tools & Techniques

| Tool / Technique | Role |
|---|---|
| 🔍 Hex Editor | Binary inspection & memory boundary identification |
| 📐 Manual Disassembly | Bytecode pattern analysis & ISA mapping |
| 🐍 Python 3 | Static VM emulator (`solver.py`) |
| 🧠 XOR Cryptanalysis | Key extraction from embedded data section |

---

## ⚠️ Disclaimer

> This writeup is for **educational purposes only**. `ram.bin` was analysed entirely statically in an isolated environment. No malicious code was executed at any point. All techniques are intended to support learning about reverse engineering and custom virtual machine internals.

---
