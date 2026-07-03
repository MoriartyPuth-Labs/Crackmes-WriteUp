# Bob's Gambling Lab

<img width="1024" height="559" alt="image" src="https://github.com/user-attachments/assets/ddef6725-2ad0-48d1-9c3f-3c11f82f75a2" />

This repository contains a comprehensive technical analysis and walkthrough for the Bob's Gambling Crackme challenge. The objective is to bypass software restrictions to clear a character's debt by exploiting common integer handling flaws.

## Challenge Information
* **Target Binary**: `crackme_bobgambling.exe` 
* **Format**: PE32+ executable (console) x86-64, Windows
* **Language**: C/C++
* **File Size**: 13,312 bytes [cite: 2]
* **Vulnerability**: Integer Overflow / Underflow 
* **Download**: https://crackmes.one/download/crackme/69b9accff2d49d8512f64a8f
* **Password**: crackmes.one

---

## Technical Analysis

### Phase 1: Initial Reconnaissance
The binary was first analyzed using the `file` command to determine its architecture and properties.

* **Command**: `file crackme_bobgambling.exe` 
* **Analysis**: The output identified the file as a 64-bit Windows console application containing 6 standard sections (.text, .rdata, .data, .pdata, .rsrc, .reloc).
* **Conclusion**: Given the small size (13KB), it was concluded that the file was likely not packed or obfuscated, allowing for straightforward static analysis.

### Phase 2: Static String Analysis
A search for readable ASCII/UTF-8 strings was performed to understand the program's logic and identify potential hidden features.

* **Command**: `strings crackme_bobgambling.exe`
* **Menu Structure**:
```
1: Payment Portal
2: Talk to a representative
-1: Admin Terminal
```
* **Key Findings**:
    * **Hidden Option**: The main menu strings revealed a hidden admin terminal at option `-1`.
    * **Security Guard**: The string "Negative values are not allowed" indicated an attempt to filter input.
    * **Developer Hint**: A PDB path was discovered: `C:\Users\prest\source\repos\crackme_intoverflow\x64\Release\crackme_bobgambling.pdb`. The inclusion of `crackme_intoverflow` in the path confirmed the specific vulnerability type.
    * **Flag Discovery**: The flag `dzctf(bob_is_free_1337)` was found directly within the binary's strings.

### Phase 3: Vulnerability Deep-Dive
The core issue is a discrepancy between the input validation check and the menu navigation logic.

* **The Flaw**: The program reads user input and attempts to block negative values. However, the guard check is inconsistent with how the `-1` option is handled in the switch statement.
* **The Mechanics**: In 64-bit C programs, input read into a 32-bit integer as `-1` is represented as `0xFFFFFFFF` in two's complement. If the guard check treats this value as unsigned, it interprets it as a large positive number, thereby bypassing the `< 0` restriction. The subsequent switch statement, however, still matches it against the `-1` case.

---

## Exploitation Walkthrough

1.  **Launch**: Execute the program in a Windows environment or via an emulator like Wine.
2.  **Input**: At the choice prompt, enter `-1`.
3.  **Bypass**: Observe that the program displays the "Negative values" error but continues to unlock the **Admin Terminal** regardless.
4.  **Execute**: Select option `1` ("Set users debt to zero").
5.  **Retrieve**: The program confirms the debt is cleared and prints the final flag.

---

## Tools Used
* **file**: Binary identification.
* **strings**: Extracting embedded printable data.
* **Static Analysis**: No dynamic debugging was required to solve this challenge.

---
**Flag**: `dzctf(bob_is_free_1337)`
