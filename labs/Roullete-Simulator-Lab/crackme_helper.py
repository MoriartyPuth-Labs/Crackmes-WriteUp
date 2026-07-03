#!/usr/bin/env python3
"""
Interactive helper for the XorShift-16 roulette crackme.
Phase 1: Bet 1 each round, enter W or L to identify the seed.
Phase 2: Tells you exactly what to bet each round to trigger integer overflow.
"""

def xorshift16(seed):
    seed = seed & 0xFFFF
    seed ^= (seed << 7) & 0xFFFF
    seed ^= (seed >> 9) & 0xFFFF
    seed ^= (seed << 8) & 0xFFFF
    return seed & 0xFFFF

def build_seed_map(rounds=30):
    seed_outcomes = {}
    for init_seed in range(1, 65536):
        s = init_seed
        outcomes = []
        for _ in range(rounds):
            s = xorshift16(s)
            outcomes.append((s % 37) < 18)
        seed_outcomes[init_seed] = tuple(outcomes)
    return seed_outcomes

def simulate_future(seed, start_round, money):
    """From a known seed state, generate bet instructions."""
    s = seed
    # Advance seed to current state
    for _ in range(start_round):
        s = xorshift16(s)
    
    instructions = []
    cur_money = money
    round_num = start_round
    
    while True:
        s = xorshift16(s)
        win = (s % 37) < 18
        round_num += 1
        
        if win:
            bet = cur_money
        else:
            bet = 1
        
        instructions.append((round_num, "WIN" if win else "LOSE", bet, cur_money))
        
        if win:
            new_money = (cur_money + bet) & 0xFFFFFFFF
            if new_money > 0x7FFFFFFF:
                new_money -= 0x100000000
            cur_money = new_money
        else:
            cur_money -= bet
        
        if cur_money < 0:
            instructions.append((round_num, "OVERFLOW -> NEGATIVE", 0, cur_money))
            break
        if cur_money == 0:
            break
        if round_num > 200000:
            break
    
    return instructions

print("=" * 60)
print("  XorShift-16 Roulette Crackme - Interactive Solver")
print("=" * 60)
print()
print("PHASE 1: Seed identification")
print("  - In the game, answer 'N' to skip rules")
print("  - Bet 1 each round for 30 rounds")
print("  - Enter W (win) or L (lose) after each round")
print()

print("Building seed database (65535 seeds x 30 rounds)...", end="", flush=True)
seed_map = build_seed_map(30)
print(" done!")
print()

# Narrow down candidates as user enters outcomes
candidates = list(range(1, 65536))
observed = []

for round_num in range(1, 31):
    while True:
        entry = input(f"Round {round_num:2d} (bet 1) - outcome? [W/L]: ").strip().upper()
        if entry in ("W", "L"):
            break
        print("  Please enter W or L")
    
    observed.append(entry == "W")
    obs_tuple = tuple(observed)
    n = len(obs_tuple)
    candidates = [s for s in candidates if seed_map[s][:n] == obs_tuple]
    
    if len(candidates) == 0:
        print("ERROR: No matching seeds! Did you mis-enter an outcome?")
        break
    elif len(candidates) == 1:
        print(f"  ✓ Seed identified after {round_num} rounds: {candidates[0]}")
        break
    else:
        print(f"  {len(candidates)} possible seeds remaining...")

if len(candidates) != 1:
    print(f"\nAfter 30 rounds, {len(candidates)} seeds remain. Using first match.")

seed = candidates[0]
print()
print("=" * 60)
print(f"PHASE 2: Exploitation (seed = {seed})")
print("=" * 60)

# Figure out current money after probe phase
money = 100
wins_in_probe = sum(1 for o in observed if o)
losses_in_probe = len(observed) - wins_in_probe
money = 100 + wins_in_probe - losses_in_probe
print(f"Your money after probe phase: {money}")
print()
print("Follow these instructions exactly:")
print()

instructions = simulate_future(seed, len(observed), money)
for (rnum, outcome, bet, mon_before) in instructions:
    if outcome == "OVERFLOW -> NEGATIVE":
        print(f"  🎉 DONE! Money overflowed to negative. You win!")
    elif outcome == "WIN":
        print(f"  Round {rnum:3d}: BET {bet:>12,}  [will WIN -> money doubles]")
    else:
        print(f"  Round {rnum:3d}: BET {bet:>12,}  [will LOSE -> safe]")
