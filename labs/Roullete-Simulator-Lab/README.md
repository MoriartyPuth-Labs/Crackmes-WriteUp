# Roulette Simulator Lab

<img width="1024" height="572" alt="image" src="https://github.com/user-attachments/assets/24a34ca0-906d-4bb9-878f-5ef8c4b97eb0" />

A complete writeup and automated solver for the **XorShift Roulette** Java crackme by Rodrigo Teixeira. This challenge involves reverse-engineering a custom 16-bit PRNG and exploiting a 32-bit integer overflow.

## 🖥️ Machine Specifications
* Author: RodrigoTeixeira
* Platform: Multiplatform
* Architecture: Java
* Language: Java
* Difficulty: 🟢 3.0/6.0
* Quality: ⭐ 4.0/5.0
* Download: https://crackmes.one/download/crackme/693c48822d267f28f69b8518
* Password: crackmes.one

## 📌 Overview
* **Platform**: Java SE 19 (Class version 63.0).
* **Objective**: Make your balance go **NEGATIVE** to win.
* **Constraint**: Bets are capped to your current balance, making a negative balance through "honest" play impossible.
* **Solution**: Identify the 16-bit XorShift seed through observation and use Java's silent integer wraparound to flip the balance.

## 🛠️ Technical Analysis

### 1. The PRNG (XorShift-16)
Bytecode analysis of the `rand()` method reveals a 3-tap XorShift algorithm:
* **Algorithm**: 
  * `seed ^= (seed << 7) & 0xFFFF`
  * `seed ^= (seed >> 9)`
  * `seed ^= (seed << 8) & 0xFFFF`
* **Seed Source**: `System.nanoTime() & 0xFFFF`.
* **State Space**: 65,535 possible values with a single cycle length of 65,535.

### 2. The Vulnerability
The game loop uses the `iadd` instruction for winning bets without performing overflow checks. 
* **Max Value**: $2,147,483,647$ (32-bit signed integer).
* **Exploit**: If `money + bet` exceeds the maximum integer value, it wraps to a negative value.
* **Threshold**: You must reach a balance of at least $1,073,741,824$ so that an "all-in" win triggers the overflow.

## 🚀 Usage

### Phase 1: Probe (Seed Recovery)
1. Start the crackme and the Python solver script.
2. Bet **1** in the game for approximately 20-30 rounds.
3. Enter the outcome (**W** for Win, **L** for Loss) into the script for each round.
4. The script compares your sequence against a precomputed map to identify the exact seed.

### Phase 2: Exploit (Overflow)
1. Once the seed is identified, follow the script's betting instructions.
2. **On Win rounds**: Bet your ENTIRE balance to achieve exponential growth.
3. **On Loss rounds**: Bet **1** to minimize losses.
4. After ~50-70 total rounds, the balance will overflow to a negative number, triggering the WIN condition.

## 📊 Summary
| Feature | Detail |
| :--- | :--- |
| **Language** | Java (Compiled .class) |
| **PRNG Type** | 16-bit XorShift |
| **Seed Space** | 65,535 (fully enumerable) |
| **Vulnerability** | Unchecked `iadd` integer overflow |
| **Rounds to Solve** | ~50 total rounds |

---
*This writeup is for educational purposes only, focusing on reverse engineering and PRNG cryptanalysis.*
