# Lab: MalwareTech VM1 — Virtual Machine Analysis
## 🖥️ Machine Specifications

* Lab name: MalwareTech VM1
* Lab Type: Static Analysis
* Languages: x86_64
* Platform: Windows 64-bit
* Difficulty: Medium
* Download: https://labs.malwaretech.com/files/virtualization/vm1.rar
* Password: MalwareTechLabs

### Overview
This lab focuses on reversing a custom 8-bit Virtual Machine (VM) used to obfuscate a hidden flag. The goal was to perform Static Analysis on the `ram.bin` file to understand the VM's internal architecture, decode its instruction set, and decrypt the flag without executing the binary.

### Technical Analysis
1. Memory Layout

By analyzing the raw hex dump (see image below), I identified the memory segmentation of the 507-byte `ram.bin` file:

* Data Section (0x00 - 0xFE): Initialized with encrypted data and space for the VM's internal state.

* Bytecode Section (0xFF - 0x1FB): The "Instruction Pointer" (IP) starts here. The VM uses a fixed-width instruction format of 3 bytes.

2. Virtual Machine Architecture

The VM follows a classic Fetch-Decode-Execute cycle. Based on the disassembly of the engine, the instruction format is:
`[Opcode (1 byte)] [Operand 1 (1 byte)] [Operand 2 (1 byte)]`

Through emulation, I mapped the following Instruction Set Architecture (ISA):
| Opcode | Instruction | Logic |
| :--- | :--- | :--- |
| 0x01 | SET | RAM[Operand1] = Operand2 |
| 0x02 | LOAD | Register = RAM[Operand1] |
| 0x03 | XOR | RAM[Operand1] = RAM[Operand1] ^ Register |

3. Emulation Logic (Pseudocode)

I derived the following logic to describe how the VM processes the bytecode:
```
counter = 0
while running:
    # 3-byte Fetch starting at offset 255
    byte_1 = bytecode[counter + 255]
    byte_2 = bytecode[counter + 256]
    byte_3 = bytecode[counter + 257]
    
    counter += 3
    decode_and_execute(byte_1, byte_2, byte_3)
```
### Solution Execution

Rather than running the malware, I wrote a Python-based emulator (solver.py) to process the ram.bin file statically. The script emulates the XOR loop hidden in the bytecode, which uses keys stored in the data section to decrypt the flag in place.

Final Flag:

`FLAG{VIRTUAL-MACHINE-UNDERSTANDING}`
