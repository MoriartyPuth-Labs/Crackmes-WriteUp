# Crackmes Writeups

Full writeups with proof-of-concept code, reproduction steps, and tooling notes.

---

## Challenge Solutions

| Challenge Name | Category | Flag / Solution |
| :--- | :--- | :--- |
| [Bob's Gambling Crackme](labs/Bobs-Gambling-Lab) | Windows PE / Integer Overflow | `dzctf(bob_is_free_1337)` |
| [Roullete Simulator](labs/Roullete-Simulator-Lab) | Java / PRNG Prediction | PRNG Seed Prediction & Wallet Overflow |
| [ChocolateFactory](labs/Willy-Wonka-Chocolate-Factory-Lab) | Windows PE / Constraint Solving | `Ch0c-M1lk-CrMe-!(L>` |
| [MalwareTech VM1](labs/MalwareTech-VM1-Lab) | Custom VM / Static Analysis | `FLAG{VIRTUAL-MACHINE-UNDERSTANDING}` |
| [CryMore](labs/CryMore-Lab) | Network Spoofing / Killswitch Bypass | Local TCP Spoofing (`HTTP/1.1 200 OK`) |
| [The Alchemist's Lock](labs/The-Alchemist-Lock-Lab) | Packer Unpacking / Binary Patching | OEP Finding & Jump Patch (`FLAG_R3v3rs3d`) |
| [Catgirl Crackme](labs/Catgirl.crack-Lab) | .NET Assembly / IL Disassembly | `Mint` (Decoy Bypass) |

---

Each folder contains a self-contained README.md writeup plus a runnable solver script or walkthrough.

```
labs/
├── Bobs-Gambling-Lab/
│   ├── README.md
│   └── bob_gambling_writeup.txt
├── Roullete-Simulator-Lab/
│   ├── README.md
│   ├── crackme_helper.py
│   └── solution.txt
├── Willy-Wonka-Chocolate-Factory-Lab/
│   ├── README.md
│   └── ChocolateFactory_writeup.txt
├── MalwareTech-VM1-Lab/
│   ├── README.md
│   └── solver.py
├── CryMore-Lab/
│   └── README.md
├── The-Alchemist-Lock-Lab/
│   └── README.md
└── Catgirl.crack-Lab/
    └── README.md
```

---

## Tooling used
- Disassembly / decompilation: IDA Pro, Ghidra, monodis (Mono IL Disassembler), Detect-It-Easy, x64dbg (with Scylla)
- Python 3: Emulator & solver scripts, keygens, custom PRNG prediction simulators
- Platform: Windows (x86/x64) and Linux/Mono runtime
- Network tools: Netcat (local TCP spoofing)

---

## Lessons / takeaways
- **Bob's Gambling Crackme** — Windows console binary; solved by abusing integer overflow / underflow logic inside the betting check.
- **Roullete Simulator** — Java class binary; solved by brute-forcing the 16-bit PRNG seed from ~20 bets to predict wins/losses and overflow the wallet balance.
- **ChocolateFactory** — 64-bit Windows console binary; solved by reconstructing a multi-stage validation algorithm and constraint solving.
- **MalwareTech VM1** — 8-bit custom Virtual Machine analysis; solved by extracting raw memory bytecode (`ram.bin`) and writing a Python VM emulator to reverse-engineer the XOR key logic.
- **CryMore** — TCP-based killswitch analysis; solved by setting up a local TCP socket using Netcat to spoof the expected response (`200 OK`) and neutralizing the logic path.
- **The Alchemist's Lock** — UPX/custom packer analysis; solved by dynamic unpacking in x64dbg, OEP dumping via Scylla, and binary patching the validation check.
- **Catgirl Crackme** — .NET assembly reversing; solved by static IL disassembly with Mono's `monodis` tool to identify the correct validation string while bypassing decoy strings.

---

## Author

<div align="center">

**Eav Puthcambo**
<br/>
AUPP Cybersecurity Programme
<br/>
American University of Phnom Penh

[![GitHub](https://img.shields.io/badge/GitHub-MoriartyPuth--Labs-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MoriartyPuth-Labs)

</div>
