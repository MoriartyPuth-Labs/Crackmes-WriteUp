<img width="1024" height="572" alt="image" src="https://github.com/user-attachments/assets/36f7d125-562c-4b97-9330-0110d61aa59d" />


# Catgirl Lab

This README provides a concise overview of the Catgirl Crackme challenge, a beginner-level .NET reverse engineering task.

## 🖥️ Machine Specifications

* Target Name: Catgirl Crackme
* Author: ended
* Platform: Unix/Linux (Windows compatible via .NET)
* Architecture: x86-64
* Language: .NET (C#)
* Difficulty: 🟢 1.0/6.0
* Quality: ⭐ 4.0/5.0
* File Size: 49.72 KB
* Download: https://crackmes.one/download/crackme/69b282cff2d49d8512f649df
* Password: crackmes.one

### Objective

The goal of this challenge is to identify the correct password hidden within a .NET assembly to trigger the "success" state of the ASCII catgirl interface.

### Tools & Methodology

* Primary Tool: `monodis` (Mono IL Disassembler).

* Secondary Tools: `strings`, `dotnet-runtime`.

* Approach: Static analysis of Intermediate Language (IL) instructions to bypass decoy strings.

## Technical Analysis

### 1. Recognition

Since the binary is a .NET assembly, standard hex editors or basic string searches often miss the logic flow. Initial reconnaissance using strings identified a potential password, but execution proved it was a distraction.

### 2. Disassembly

Using `monodis CatgirlCrack.dll`, I examined the `Program::Main` method. The IL code revealed two distinct string comparisons:

* The Decoy (`meow`): Located at `IL_0045`. Entering this triggers a "wrong guess" handler.

* The Flag (`Mint`): Found at `IL_0026`. This is the literal string required by the `System.String::Equals` method to satisfy the success condition.

### 3. Validation

Running the binary and providing the discovered key:
```
$ ./CatgirlCrack
Enter the password below =^_^=: Mint
Mrrooww! Good Kitty! Mwwwaaah~!
```
### Expected Results

* Input: `Mint`
* Output: `Mrrooww! Good Kitty! Mwwwaaah~!`
