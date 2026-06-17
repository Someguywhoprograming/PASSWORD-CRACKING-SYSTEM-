import random
import time
import string
import os
import itertools
import time
import sys

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def matrix_effect(seconds=3):
    chars = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&@"
    end_time = time.time() + seconds
    while time.time() < end_time:
        print("".join(random.choice(chars) for _ in range(90)))
        time.sleep(0.03)

def hacker_loading_screen():
    clear()

    banner = r"""
███╗   ███╗██████╗     ██████╗  ██████╗ ██████╗  ██████╗ ████████╗
████╗ ████║██╔══██╗    ██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗╚══██╔══╝
██╔████╔██║██████╔╝    ██████╔╝██║   ██║██████╔╝██║   ██║   ██║
██║╚██╔╝██║██╔══██╗    ██╔══██╗██║   ██║██╔══██╗██║   ██║   ██║
██║ ╚═╝ ██║██║  ██║    ██║  ██║╚██████╔╝██████╔╝╚██████╔╝   ██║
╚═╝     ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝    ╚═╝

    PASSWORD CRACKING SYSTEM v1.0
"""

    print(banner)

    matrix_effect(2)

    messages = [
        "Initializing secure terminal...",
        "Connecting to underground network...",
        "Scanning open ports...",
        "Bypassing firewall...",
        "Decrypting database...",
        "Establishing root access...",
        "Access granted."
    ]

def loading_spinner(mp=3):
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    end_time = time.time() + mp
    
    while time.time() < end_time:
        sys.stdout.write("\rLoading " + next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)

    print("\rDone!       ")

loading_spinner(5)

# ====================== PASSWORD GENERATION ======================

def generate_password(difficulty, pw_type):
    if pw_type == "word":
        words = ["secret", "password", "apple", "banana", "doggo", "cat", "python", "hack", "virus", "shadow", 
                "dragon", "ninja", "matrix", "zeus", "odin", "thor", "admin", "welcome", "letmein", "qwerty"]
        if difficulty == 1:   # Easy
            return random.choice(words)
        elif difficulty == 2: # Medium
            return random.choice(words) + str(random.randint(10, 99))
        else:                 # Hard
            return random.choice(words) + random.choice(words) + str(random.randint(100, 999))
    
    elif pw_type == "number":
        if difficulty == 1:
            return ''.join(random.choices(string.digits, k=4))
        elif difficulty == 2:
            return ''.join(random.choices(string.digits, k=6))
        else:
            return ''.join(random.choices(string.digits, k=8))
    
    else:  # "fingerprint"
        if difficulty == 1:
            pattern = ['●', '○', '◐', '◑']
            return ''.join(random.choices(pattern, k=5))
        elif difficulty == 2:
            pattern = ['●', '○', '◐', '◑', '◆', '◇']
            return ''.join(random.choices(pattern, k=7))
        else:
            pattern = ['●', '○', '◐', '◑', '◆', '◇', '★', '☆']
            return ''.join(random.choices(pattern, k=9))

# ====================== CRACKING METHODS ======================

def brute_force(password, difficulty):
    print(f"\n🔨 Starting Brute Force attack... ({len(password)} characters)")
    attempts = 0
    chars = string.ascii_lowercase + string.digits
    
    max_attempts = 500 if difficulty == 3 else 200 if difficulty == 2 else 50
    
    for _ in range(max_attempts):
        guess = ''.join(random.choices(chars, k=len(password)))
        attempts += 1
        if attempts % 15 == 0:
            print(f"  Tried: {guess} ({attempts} attempts)", end="\r")
        if guess == password:
            print(f"\n✅ SUCCESS! Password cracked in {attempts} attempts!")
            return True
        time.sleep(0.03)
    print("\n⏳ Brute force was too slow...")
    return False

def dictionary_attack(password):
    print("\n📖 Starting Dictionary attack...")
    common_words = ["admin", "password", "123456", "qwerty", "letmein", "welcome", "secret", "dragon", 
                   "ninja", "shadow", "master", "monkey"]
    time.sleep(1)
    
    for word in common_words + [password]:
        print(f"  Trying: {word}")
        time.sleep(0.4)
        if word == password:
            print("✅ Found in dictionary!")
            return True
    print("❌ Not found in dictionary.")
    return False

def fingerprint_crack(real_pattern):
    print("\n🔍 Fingerprint Scanner starting...")
    print(f"Target pattern: {real_pattern}")
    print("Try to match it!\n")
    
    for i in range(5):
        guess = input(f"Attempt {i+1}: ").strip()
        if guess == real_pattern:
            print("✅ Fingerprint matched!")
            return True
        else:
            matches = sum(1 for a, b in zip(guess, real_pattern) if a == b)
            print(f"   {matches}/{len(real_pattern)} symbols match")
    print("❌ Fingerprint scan failed.")
    return False

# ====================== MAIN GAME ======================

def play_game():
    clear()
    print("="*60)
    print("🔐 PASSWORD CRACKING GAME 🔐".center(60))
    print("="*60)
    
    print("\nDifficulty Levels:")
    print("1. Easy     (Beginner)")
    print("2. Medium   (Normal)")
    print("3. Hard     (Expert)")
    
    while True:
        try:
            diff = int(input("\nChoose difficulty (1-3): "))
            if 1 <= diff <= 3:
                break
        except:
            pass
        print("Please enter 1, 2 or 3!")

    types = ["word", "number", "fingerprint"]
    pw_type = random.choice(types)
    
    password = generate_password(diff, pw_type)
    
    print(f"\n🎯 Target Type: **{pw_type.upper()}**")
    print(f"Difficulty: {'★' * diff}")
    print("-" * 50)
    
    attempts_left = 5 if diff == 1 else 4 if diff == 2 else 3
    
    while attempts_left > 0:
        print(f"\nYou have {attempts_left} attempts left.")
        print("1. Brute Force")
        print("2. Dictionary Attack")
        if pw_type == "fingerprint":
            print("3. Fingerprint Scan")
        else:
            print("3. Direct Guess")
        
        choice = input("\nChoose attack method (1-3): ")
        
        success = False
        if choice == "1":
            success = brute_force(password, diff)
        elif choice == "2":
            success = dictionary_attack(password)
        elif choice == "3":
            if pw_type == "fingerprint":
                success = fingerprint_crack(password)
            else:
                guess = input("Enter the password: ")
                if guess == password:
                    success = True
                    print("🎉 Congratulations! You cracked it!")
        
        if success:
            print(f"\n🏆 MISSION SUCCESS! The password was: {password}")
            break
        
        attempts_left -= 1
        if attempts_left > 0:
            print("Try again with a different method!")
    
    if attempts_left == 0:
        print(f"\n💥 Mission Failed. The password was: {password}")

    input("\nPress Enter to continue...")

# ====================== START ======================

if __name__ == "__main__":
    hacker_loading_screen()
    while True:
        play_game()
        if input("\nPlay again? (y/n): ").lower() != 'y':
            print("Thanks for playing! Goodbye!")
            break