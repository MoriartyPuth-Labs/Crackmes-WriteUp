<div align="center">

# 🫧 Lab: MalwareTech VM1 — Virtual Machine Analysis

<img src="https://github.com/user-attachments/assets/19167dcc-61d3-4a5d-b8f2-b58f9ccb4c04" width="860" alt="MalwareTech VM1 Banner"/>

<br/>

![Platform](https://img.shields.io/badge/Platform-MalwareTech%20Labs-blue?style=for-the-badge&logo=windows&logoColor=white)
![Type](https://img.shields.io/badge/Type-Static%20Analysis-purple?style=for-the-badge)
![Arch](https://img.shields.io/badge/Architecture-x86__64-informational?style=for-the-badge&logo=intel&logoColor=white)
![Difficulty](https://img.shields.io/badge/Difficulty-Medium-yellow?style=for-the-badge)
![Language](https://img.shields.io/badge/Solver-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flag](https://img.shields.io/badge/Flag-Captured%20🏆-success?style=for-the-badge)

</div>

---

## 📌 About

This lab focuses on reversing a **custom 8-bit Virtual Machine (VM)** used to obfuscate a hidden flag inside a 507-byte binary (`ram.bin`). The goal was to perform **pure static analysis** — understanding the VM's internal architecture, mapping its instruction set, and decrypting the flag without ever executing the binary.

| Field | Details |
|---|---|
| 🖥️ Lab Name | MalwareTech VM1 |
| 🔬 Lab Type | Static Analysis |
| ⚙️ Architecture | x86_64 |
| 🪟 Platform | Windows 64-bit |
| ⚡ Difficulty | Medium |
| 📦 Download | [vm1.rar](https://labs.malwaretech.com/files/virtualization/vm1.rar) |
| 🔑 Password | `MalwareTechLabs` |
| 🏆 Flag | `FLAG{VIRTUAL-MACHINE-UNDERSTANDING}` |

---

## 🗺️ Analysis Chain

```
[Load ram.bin] → [Hex Dump Analysis] → [Memory Layout Mapping]
    → [ISA Reconstruction] → [Fetch-Decode-Execute Emulation]
        → [XOR Key Extraction] → [Python Emulator] → [FLAG 🏆]
```

---

## 🔬 Technical Analysis

### 1️⃣ Memory Layout

Opening `ram.bin` in a hex editor revealed a clean split between data and code within the 507-byte file.

<img src="https://github.com/user-attachments/assets/ead45377-ead3-40bc-a98a-cd497ec982f3" width="800" alt="Hex dump memory layout"/>

| Region | Offset Range | Description |
|---|---|---|
| 📦 Data Section | `0x00` – `0xFE` | Initialized with encrypted data + VM internal state |
| ⚙️ Bytecode Section | `0xFF` – `0x1FB` | Instruction Pointer (IP) starts here |

> The VM uses a **fixed-width 3-byte instruction format** throughout the entire bytecode section.

---

### 2️⃣ Virtual Machine Architecture

The VM operates on a classic **Fetch → Decode → Execute** cycle. Each instruction follows the format:

```
┌────────────────┬─────────────────┬─────────────────┐
│  Opcode        │   Operand 1     │   Operand 2     │
│  (1 byte)      │   (1 byte)      │   (1 byte)      │
└────────────────┴─────────────────┴─────────────────┘
```

Through manual emulation and bytecode tracing, the full **Instruction Set Architecture (ISA)** was reconstructed:

| Opcode | Mnemonic | Operation |
|---|---|---|
| `0x01` | **SET** | `RAM[Operand1] = Operand2` |
| `0x02` | **LOAD** | `Register = RAM[Operand1]` |
| `0x03` | **XOR** | `RAM[Operand1] = RAM[Operand1] ^ Register` |

---

### 3️⃣ Fetch-Decode-Execute Loop (Pseudocode)

The VM reads 3 bytes at a time starting at offset `0xFF` (decimal 255), advancing the counter by 3 on each cycle:

```python
counter = 0

while running:
    # Fetch — 3-byte instruction at offset 255
    byte_1 = bytecode[counter + 255]   # Opcode
    byte_2 = bytecode[counter + 256]   # Operand 1
    byte_3 = bytecode[counter + 257]   # Operand 2

    counter += 3

    decode_and_execute(byte_1, byte_2, byte_3)
```

---

### 4️⃣ Static Emulator — `solver.py`

Rather than executing the binary, a **Python-based static emulator** was written to process `ram.bin` entirely in userspace. The script:

1. Loads `ram.bin` into a byte array
2. Parses the bytecode section starting at `0xFF`
3. Emulates `SET`, `LOAD`, and `XOR` operations against the data section
4. Extracts the XOR keys embedded in the data section
5. Decrypts the flag in place and prints the result

```python
ram = bytearray(open("ram.bin", "rb").read())

register = 0
counter  = 0
BYTECODE_START = 0xFF

while True:
    ip = BYTECODE_START + counter
    if ip + 2 >= len(ram):
        break

    opcode, op1, op2 = ram[ip], ram[ip + 1], ram[ip + 2]
    counter += 3

    if opcode == 0x01:          # SET
        ram[op1] = op2
    elif opcode == 0x02:        # LOAD
        register = ram[op1]
    elif opcode == 0x03:        # XOR
        ram[op1] ^= register
    else:
        break                   # HALT

# Extract and print the decrypted flag
print("Flag:", bytes(ram[0:0xFF]).split(b"\x00")[0].decode())
```

---

## 🏆 Flag

<div align="center">

```
██╗   ██╗███╗   ███╗ ██╗
██║   ██║████╗ ████║ ╚═╝
██║   ██║██╔████╔██║ ██╗
╚██╗ ██╔╝██║╚██╔╝██║ ██║
 ╚████╔╝ ██║ ╚═╝ ██║ ██║
  ╚═══╝  ╚═╝     ╚═╝ ╚═╝

FLAG{VIRTUAL-MACHINE-UNDERSTANDING}
```

</div>

---

## 🧰 Tools Used

| Tool | Purpose |
|---|---|
| 🔍 Hex Editor | Raw binary inspection & memory layout mapping |
| 🐍 Python | Static VM emulator (`solver.py`) |
| 📊 Manual Disassembly | ISA reconstruction from bytecode patterns |

---

## ⚠️ Disclaimer

> This writeup is for **educational purposes only**. The binary was analysed entirely statically in an isolated environment. All techniques described are intended to support learning about reverse engineering and virtual machine internals.

---
