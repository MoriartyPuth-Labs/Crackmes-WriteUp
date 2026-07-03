import os

def solve_vm1(file_path):
    """
    Emulates the MalwareTech VM1 logic to decrypt the hidden flag.
    
    The VM has 255 bytes of RAM and starts executing bytecode at offset 255.
    Instruction format: [Opcode (1 byte)] [Operand 1 (1 byte)] [Operand 2 (1 byte)]
    """
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "rb") as f:
        ram = bytearray(f.read())

    # VM state
    pc = 0xFF        # Instruction Pointer starts at 255
    reg = 0          # 8-bit temporary register
    running = True

    print("[*] Starting VM Emulation...")

    while running and pc + 2 < len(ram):
        # Fetch 3 bytes
        opcode = ram[pc]
        arg1 = ram[pc + 1]
        arg2 = ram[pc + 2]
        
        # Increment PC by 3 (Fetch-Decode-Execute cycle)
        pc += 3

        # Instruction Set Architecture (ISA) Logic
        if opcode == 0x01:   # SET / ASSIGN
            ram[arg1] = arg2
        elif opcode == 0x02: # LOAD
            reg = ram[arg1]
        elif opcode == 0x03: # XOR
            ram[arg1] ^= reg
        else:                # Any other opcode acts as a HALT
            running = False

    # The flag is stored in the first part of the RAM after decryption
    # Based on the bytecode, it's usually at the very beginning
    flag = ""
    for b in ram[:0x22]: # Reading first 34 bytes
        if 32 <= b <= 126: # Filter for printable ASCII
            flag += chr(b)
    
    print(f"[*] Emulation complete.")
    print(f"[+] Flag found: {flag.strip()}")

if __name__ == "__main__":
    # Ensure ram.bin is in the same directory
    solve_vm1("ram.bin")
