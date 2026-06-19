import base64
import hashlib
import json
import os
import random
import time
import tkinter as tk
from tkinter import colorchooser, messagebox, scrolledtext, simpledialog

try:
    import winsound
except ImportError:
    winsound = None


HIGHSCORE_FILE = "highscores.json"
ACHIEVEMENT_FILE = "achievements.json"
PROGRESS_FILE = "player_progress.json"


class CTFPasswordCracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CTF Password Cracking Challenge")
        self.root.geometry("1180x820")
        self.root.configure(bg="#070707")

        self.bg_color = "#070707"
        self.text_color = "#00ff41"
        self.warning_color = "#ffcc00"
        self.fullscreen = False

        self.highscores = self.load_json(HIGHSCORE_FILE, [])
        self.unlocked_achievements = self.load_json(ACHIEVEMENT_FILE, [])
        self.progress = self.load_json(PROGRESS_FILE, {})
        self.xp = self.progress.get("xp", 0)
        self.rank = self.progress.get("rank", "Script Kiddie")
        self.unlocked_methods = set(self.progress.get("unlocked_methods", ["dictionary"]))
        self.inventory = set(self.progress.get("inventory", []))
        self.campaign_index = self.progress.get("campaign_index", 0)
        self.difficulty = self.progress.get("difficulty", "normal")
        self.language = self.progress.get("language", "en")
        self.root.title("CTF Password Cracking Challenge" if self.language == "en" else "CTF Jelszotores Kihivas")
        self.stats = self.default_stats()
        self.stats.update(self.progress.get("stats", {}))

        self.targets = self.build_targets()
        self.boss_target = self.build_boss_target()
        self.puzzles = self.build_puzzles()
        self.shop_items = self.build_shop_items()

        self.current_target = None
        self.password = ""
        self.revealed = ""
        self.clues_seen = 0
        self.attempts = 0
        self.alert_level = 0
        self.start_time = None
        self.score = 0
        self.active_puzzle = None
        self.campaign_mode = False
        self.boss_phase = 0
        self.used_hint = False
        self.game_over = False

        self.log = None
        self.cmd_entry = None
        self.info_label = None
        self.cursor_label = None
        self.cursor_on = True

        self.root.bind("<Escape>", lambda _event: self.toggle_fullscreen(False))
        self.refresh_unlocks()
        self.show_main_menu()
        self.blink_cursor()

    def default_stats(self):
        return {
            "missions_completed": 0,
            "campaign_completed": 0,
            "puzzles_solved": 0,
            "total_time": 0.0,
            "best_score": 0,
            "favorite_attack": {},
        }

    def build_targets(self):
        return [
            {
                "name": "ShadowDragon87",
                "backstory": "Forum admin. Old profiles say he was born in 1998 and constantly posts about his cat.",
                "backstory_hu": "Forum admin. Regi profiljai szerint 1998-ban szuletett, es mindig a macskajarol posztol.",
                "profile": [
                    "Old bio: birthday party photos tagged 1998.",
                    "Pet account: Luna the cat.",
                    "Nickname in game chats: shadow.",
                    "Fake lead: favorite color is green.",
                ],
                "leaks": [
                    "Leaked note: birthday first, pet second.",
                    "Recovered username fragment: dragon87.",
                ],
                "pattern": "birth_year + pet",
                "parts": {"birth_year": "1998", "pet": "luna", "nickname": "shadow"},
                "generator": lambda p: p["birth_year"] + p["pet"],
            },
            {
                "name": "NeonViper",
                "backstory": "Zero-day dealer. He mixes his nickname with a favorite number in passwords.",
                "backstory_hu": "Zero-day kereskedo. A becenevet es egy kedvenc szamot keveri a jelszavaiba.",
                "profile": [
                    "Handle history: Viper, NeonV, NViper.",
                    "Favorite number in leaked game profile: 42.",
                    "Dog name from a deleted post: Bolt.",
                    "Fake lead: birth year 2001.",
                ],
                "leaks": [
                    "Paste title: viper credentials test.",
                    "Comment: lucky number comes last.",
                ],
                "pattern": "nickname + favorite_number",
                "parts": {"nickname": "viper", "favorite_number": "42", "pet": "bolt"},
                "generator": lambda p: p["nickname"] + p["favorite_number"],
            },
            {
                "name": "CryptoReaper",
                "backstory": "Ransomware operator. Uses company nicknames and years in passwords.",
                "backstory_hu": "Ransomware operator. Vallalati beceneveket es evszamokat hasznal.",
                "profile": [
                    "Old employer: Acme Security.",
                    "First public malware sample: 2019.",
                    "Forum signature: Reap what you encrypt.",
                    "Fake lead: pet name is Rex.",
                ],
                "leaks": [
                    "Archive tag: acme incident.",
                    "Timeline note: first sample year matters.",
                ],
                "pattern": "company + sample_year",
                "parts": {"company": "acme", "sample_year": "2019", "pet": "rex"},
                "generator": lambda p: p["company"] + p["sample_year"],
            },
            {
                "name": "GhostByte",
                "backstory": "State-backed operator. Pairs a city name with an animal codename.",
                "backstory_hu": "Allami hatteru operator. Varosnevet es allatos kodnevet parosit.",
                "profile": [
                    "Travel cache: Berlin login cluster.",
                    "Codename in leaked ticket: Raven.",
                    "Old nickname: ByteGhost.",
                    "Fake lead: lucky number 77.",
                ],
                "leaks": [
                    "Flight cache: berlin repeated three times.",
                    "Internal codename appears after city.",
                ],
                "pattern": "city + codename",
                "parts": {"city": "berlin", "codename": "raven", "number": "77"},
                "generator": lambda p: p["city"] + p["codename"],
            },
            {
                "name": "VoidWalker",
                "backstory": "Anonymous sysadmin. Always leaves a symbol at the end of passwords.",
                "backstory_hu": "Anonim sysadmin. A jelszavak vegen mindig szimbolumot hagy.",
                "profile": [
                    "Badge ID fragment: 7314.",
                    "Pinned note says: remember the hashbang.",
                    "Usual symbol: !",
                    "Fake lead: favorite city Tokyo.",
                ],
                "leaks": [
                    "Access badge leak: 7314.",
                    "Shell habit: symbol at the end.",
                ],
                "pattern": "badge_fragment + symbol",
                "parts": {"badge_fragment": "7314", "symbol": "!"},
                "generator": lambda p: p["badge_fragment"] + p["symbol"],
            },
        ]

    def build_boss_target(self):
        return {
            "name": "The Architect",
            "backstory": "The final campaign target. The password has multiple layers, each CTF task gives one fragment.",
            "backstory_hu": "A kampany vegso celpontja. A jelszo tobb retegbol epul, minden CTF feladat egy darabot ad.",
            "profile": [
                "Base alias: architect.",
                "Old project year: 2026.",
                "Signature symbol: #.",
                "Fake lead: favorite pet is Nova.",
            ],
            "leaks": [
                "Boss pattern requires alias, year, symbol.",
                "No single attack solves the whole chain.",
            ],
            "pattern": "alias + project_year + symbol",
            "parts": {"alias": "architect", "project_year": "2026", "symbol": "#"},
            "generator": lambda p: p["alias"] + p["project_year"] + p["symbol"],
            "boss_phases": ["base64", "caesar", "morse", "sql"],
        }

    def build_puzzles(self):
        return [
            {"type": "base64", "title": "Base64 decode", "question": "Decode this: c2hhZG93", "answer": "shadow", "reward": 25},
            {"type": "caesar", "title": "Caesar cipher", "question": "Caesar -3: kdyhq", "answer": "haven", "reward": 30},
            {"type": "morse", "title": "Morse code", "question": "--. .... --- ... -", "answer": "ghost", "reward": 30},
            {"type": "qr", "title": "Text QR puzzle", "question": "Mini QR note: [black white black] = answer is tunnel", "answer": "tunnel", "reward": 35},
            {"type": "sql", "title": "SQL injection puzzle", "question": "Login bypass payload: admin' __ '1'='1  (missing operator)", "answer": "or", "reward": 40},
        ]

    def build_shop_items(self):
        return {
            "hash_analyzer": {"cost": 80, "desc": "hash command reveals one extra character."},
            "metadata_scanner": {"cost": 120, "desc": "scan leaks has lower alert cost."},
            "social_scraper": {"cost": 150, "desc": "profile command reveals all profile lines."},
            "pattern_predictor": {"cost": 220, "desc": "predict command can reveal password structure."},
            "proxy_shield": {"cost": 180, "desc": "random alert spikes are reduced."},
        }

    def load_json(self, path, fallback):
        if not os.path.exists(path):
            return fallback
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return fallback

    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def save_progress(self):
        self.save_json(
            PROGRESS_FILE,
            {
                "xp": self.xp,
                "rank": self.rank,
                "unlocked_methods": sorted(self.unlocked_methods),
                "inventory": sorted(self.inventory),
                "campaign_index": self.campaign_index,
                "difficulty": self.difficulty,
                "language": self.language,
                "stats": self.stats,
            },
        )

    def tr(self, key):
        texts = {
            "campaign_mission": {"en": "CAMPAIGN MISSION", "hu": "KAMPANY KULDETES"},
            "random_mission": {"en": "RANDOM MISSION", "hu": "VELETLEN KULDETES"},
            "black_market": {"en": "BLACK MARKET", "hu": "FEKETE PIAC"},
            "player_stats": {"en": "PLAYER STATS", "hu": "JATEKOS STATOK"},
            "high_scores": {"en": "HIGH SCORES", "hu": "DICSOSEGLISTA"},
            "achievements": {"en": "ACHIEVEMENTS", "hu": "EREDMENYEK"},
            "help_commands": {"en": "HELP / COMMANDS", "hu": "SUGO / PARANCSOK"},
            "settings": {"en": "SETTINGS", "hu": "BEALLITASOK"},
            "exit": {"en": "EXIT", "hu": "KILEPES"},
            "rank": {"en": "Rank", "hu": "Rang"},
            "campaign": {"en": "Campaign", "hu": "Kampany"},
            "difficulty": {"en": "Difficulty", "hu": "Nehezseg"},
            "help": {"en": "HELP", "hu": "SUGO"},
            "full": {"en": "FULL", "hu": "TELJES"},
            "menu": {"en": "MENU", "hu": "MENU"},
            "command": {"en": "COMMAND >", "hu": "PARANCS >"},
            "current": {"en": "Current", "hu": "Aktualis"},
            "alert": {"en": "Alert", "hu": "Riasztas"},
            "attempts": {"en": "Attempts", "hu": "Probak"},
            "time": {"en": "Time", "hu": "Ido"},
            "methods": {"en": "Methods", "hu": "Modszerek"},
            "language": {"en": "Language", "hu": "Nyelv"},
            "english": {"en": "English", "hu": "Angol"},
            "hungarian": {"en": "Hungarian", "hu": "Magyar"},
            "background_color": {"en": "Background Color", "hu": "Hatter szine"},
            "text_color": {"en": "Text Color", "hu": "Szoveg szine"},
            "reset_colors": {"en": "Reset Colors", "hu": "Szinek visszaallitasa"},
            "difficulty_easy": {"en": "Difficulty: Easy", "hu": "Nehezseg: Konnyu"},
            "difficulty_normal": {"en": "Difficulty: Normal", "hu": "Nehezseg: Normal"},
            "difficulty_hard": {"en": "Difficulty: Hard", "hu": "Nehezseg: Nehez"},
            "secure_terminal": {"en": "Secure terminal online...", "hu": "Biztonsagos terminal online..."},
            "mode": {"en": "MODE", "hu": "MOD"},
            "target": {"en": "TARGET", "hu": "CELPONT"},
            "profile": {"en": "PROFILE", "hu": "PROFIL"},
            "pattern": {"en": "PATTERN", "hu": "MINTA"},
            "status": {"en": "STATUS", "hu": "ALLAPOT"},
            "cracking": {"en": "CRACKING...", "hu": "TORES FOLYAMATBAN..."},
            "intro_help": {
                "en": "Use scan profile, scan leaks, puzzle, build, attack, submit.",
                "hu": "Hasznald: scan profile, scan leaks, puzzle, build, attack, submit.",
            },
            "boss_intro": {
                "en": "Boss chain active. Solve boss phases with: boss",
                "hu": "Boss lanc aktiv. A fazisok megoldasa: boss",
            },
        }
        return texts.get(key, {}).get(self.language, texts.get(key, {}).get("en", key))

    def set_language(self, language):
        if language not in {"en", "hu"}:
            return
        self.language = language
        self.save_progress()
        self.root.title("CTF Password Cracking Challenge" if language == "en" else "CTF Jelszotores Kihivas")
        self.show_main_menu()

    def target_text(self, target, key):
        if self.language == "hu":
            return target.get(f"{key}_hu", target.get(key, ""))
        return target.get(key, "")

    def play_sound(self, sound_type):
        if winsound:
            patterns = {
                "typing": [(900, 18)],
                "success": [(784, 90), (988, 90), (1175, 140)],
                "fail": [(220, 180), (160, 220)],
                "alarm": [(880, 100), (440, 100), (880, 100), (440, 180)],
                "access": [(523, 90), (659, 90), (784, 90), (1046, 220)],
            }
            for freq, duration in patterns.get(sound_type, [(500, 80)]):
                winsound.Beep(freq, duration)
            return
        try:
            self.root.bell()
        except tk.TclError:
            pass

    def rank_for_xp(self):
        if self.xp >= 500:
            return "Ghost"
        if self.xp >= 250:
            return "Elite"
        if self.xp >= 100:
            return "Hacker"
        return "Script Kiddie"

    def refresh_unlocks(self):
        for required_xp, method in [(0, "dictionary"), (100, "john"), (180, "hydra"), (250, "mask"), (500, "ghost")]:
            if self.xp >= required_xp:
                self.unlocked_methods.add(method)
        new_rank = self.rank_for_xp()
        if new_rank != self.rank:
            self.rank = new_rank
            self.log_msg(f"[RANK UP] New rank: {self.rank}", sound="success")

    def add_xp(self, amount):
        if amount:
            self.xp += amount
            self.log_msg(f"[XP] +{amount} XP", sound="success")
        self.refresh_unlocks()
        self.save_progress()
        self.update_info_label()

    def show_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=self.bg_color)

        banner = (
            "  ____ _____ _____   ____ ____      _    ____ _  _______ ____  \n"
            " / ___|_   _|  ___| / ___|  _ \\    / \\  / ___| |/ / ____|  _ \\ \n"
            "| |     | | | |_   | |   | |_) |  / _ \\| |   | ' /|  _| | |_) |\n"
            "| |___  | | |  _|  | |___|  _ <  / ___ \\ |___| . \\| |___|  _ < \n"
            " \\____| |_| |_|     \\____|_| \\_\\/_/   \\_\\____|_|\\_\\_____|_| \\_\\"
        )
        tk.Label(self.root, text=banner, font=("Courier", 11, "bold"), fg=self.text_color, bg=self.bg_color, justify=tk.LEFT).pack(pady=18)
        tk.Label(
            self.root,
            text=f"{self.tr('rank')}: {self.rank} | XP: {self.xp} | {self.tr('campaign')}: {self.campaign_index}/{len(self.targets)} | {self.tr('difficulty')}: {self.difficulty}",
            font=("Courier", 12),
            fg=self.warning_color,
            bg=self.bg_color,
        ).pack(pady=6)

        button_style = {"font": ("Courier", 14, "bold"), "fg": "white", "width": 30, "height": 2}
        tk.Button(self.root, text=self.tr("campaign_mission"), bg="#b00020", command=lambda: self.start_mission(True), **button_style).pack(pady=7)
        tk.Button(self.root, text=self.tr("random_mission"), bg="#8b1e3f", command=lambda: self.start_mission(False), **button_style).pack(pady=7)
        tk.Button(self.root, text=self.tr("black_market"), bg="#7a4f00", command=self.show_shop, **button_style).pack(pady=7)
        tk.Button(self.root, text=self.tr("player_stats"), bg="#36558f", command=self.show_player_stats, **button_style).pack(pady=7)
        tk.Button(self.root, text=self.tr("high_scores"), bg="#147a32", command=self.show_highscores, **button_style).pack(pady=7)
        tk.Button(self.root, text=self.tr("achievements"), bg="#6a4c93", command=self.show_achievements, **button_style).pack(pady=7)
        tk.Button(self.root, text=self.tr("help_commands"), bg="#0066aa", command=self.show_help_commands, **button_style).pack(pady=7)
        tk.Button(self.root, text=self.tr("settings"), bg="#444444", command=self.open_settings, **button_style).pack(pady=7)
        tk.Button(self.root, text=self.tr("exit"), bg="#555555", command=self.root.quit, **button_style).pack(pady=12)

    def start_mission(self, campaign=False):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=self.bg_color)

        self.campaign_mode = campaign
        if campaign and self.campaign_index >= len(self.targets):
            self.current_target = self.boss_target
            self.boss_phase = 0
        elif campaign:
            self.current_target = self.targets[self.campaign_index]
            self.boss_phase = -1
        else:
            self.current_target = random.choice(self.targets)
            self.boss_phase = -1

        self.password = self.current_target["generator"](self.current_target["parts"])
        self.revealed = self.get_initial_reveal()
        self.clues_seen = 0
        self.attempts = 0
        self.alert_level = {"easy": 0, "normal": 10, "hard": 20}.get(self.difficulty, 10)
        self.start_time = time.time()
        self.score = 0
        self.active_puzzle = None
        self.used_hint = False
        self.game_over = False

        top_bar = tk.Frame(self.root, bg=self.bg_color)
        top_bar.pack(fill="x", padx=20, pady=(12, 0))
        tk.Button(top_bar, text=self.tr("help"), font=("Courier", 11, "bold"), bg="#0066aa", fg="white", command=self.show_help_commands).pack(side=tk.RIGHT, padx=4)
        tk.Button(top_bar, text=self.tr("full"), font=("Courier", 11, "bold"), bg="#222222", fg=self.text_color, command=self.toggle_fullscreen).pack(side=tk.RIGHT, padx=4)
        tk.Button(top_bar, text=self.tr("menu"), font=("Courier", 11, "bold"), bg="#444444", fg="white", command=self.show_main_menu).pack(side=tk.RIGHT, padx=4)

        self.log = scrolledtext.ScrolledText(self.root, bg="#000000", fg=self.text_color, insertbackground=self.text_color, font=("Courier", 10), relief=tk.FLAT, borderwidth=0)
        self.log.pack(fill=tk.BOTH, expand=True, padx=20, pady=14)

        self.info_label = tk.Label(self.root, fg=self.warning_color, bg=self.bg_color, font=("Courier", 11))
        self.info_label.pack(pady=3)

        cmd_frame = tk.Frame(self.root, bg=self.bg_color)
        cmd_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(cmd_frame, text=self.tr("command"), font=("Courier", 12, "bold"), fg=self.warning_color, bg=self.bg_color).pack(side=tk.LEFT)
        self.cmd_entry = tk.Entry(cmd_frame, font=("Courier", 12), bg="#111111", fg=self.text_color, insertbackground=self.text_color)
        self.cmd_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=10)
        self.cmd_entry.bind("<Return>", self.process_command)
        self.cursor_label = tk.Label(cmd_frame, text="_", font=("Courier", 14, "bold"), fg=self.text_color, bg=self.bg_color)
        self.cursor_label.pack(side=tk.LEFT)
        self.cmd_entry.focus_set()

        self.update_info_label()
        self.print_intro()

    def print_intro(self):
        md5_hash, sha_hash = self.get_hashes(self.password)
        mission_type = "BOSS FIGHT" if self.current_target == self.boss_target else ("CAMPAIGN" if self.campaign_mode else "RANDOM")
        lines = [
            "SHADOWREALM OS v6.0",
            self.tr("secure_terminal"),
            "",
            f"{self.tr('mode'):<7}: {mission_type}",
            f"{self.tr('target'):<7}: {self.current_target['name']}",
            f"{self.tr('profile'):<7}: {self.target_text(self.current_target, 'backstory')}",
            f"{self.tr('pattern'):<7}: {self.current_target['pattern']}",
            "",
            f"MD5     : {md5_hash}",
            f"SHA256  : {sha_hash}",
            f"{self.tr('status'):<7}: {self.tr('cracking')}",
            "",
            self.tr("intro_help"),
        ]
        if self.current_target == self.boss_target:
            lines.append(self.tr("boss_intro"))
        self.type_lines(lines)

    def type_lines(self, lines):
        def worker(index=0):
            if not self.log or index >= len(lines):
                return
            self.type_text(lines[index] + "\n", lambda: worker(index + 1))
        worker()

    def type_text(self, text, done=None, pos=0):
        if not self.log:
            return
        if pos >= len(text):
            if done:
                self.root.after(35, done)
            return
        self.log.insert(tk.END, text[pos])
        self.log.see(tk.END)
        if text[pos].strip() and random.random() < 0.16:
            self.play_sound("typing")
        self.root.after(7, lambda: self.type_text(text, done, pos + 1))

    def log_msg(self, message, delay=0, sound=None):
        if sound:
            self.play_sound(sound)
        if not self.log:
            return
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        if delay:
            self.root.update()
            time.sleep(delay)

    def blink_cursor(self):
        if self.cursor_label and self.cursor_label.winfo_exists():
            self.cursor_on = not self.cursor_on
            self.cursor_label.config(text="_" if self.cursor_on else " ")
        self.root.after(450, self.blink_cursor)

    def get_initial_reveal(self):
        hidden = ["_"] * len(self.password)
        if len(hidden) > 3:
            hidden[0] = self.password[0]
            hidden[-1] = self.password[-1]
        return "".join(hidden)

    def get_hashes(self, password):
        md5_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
        sha_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()[:32] + "..."
        return md5_hash, sha_hash

    def update_info_label(self):
        if not self.info_label:
            return
        elapsed = time.time() - self.start_time if self.start_time else 0
        methods = ", ".join(sorted(self.unlocked_methods))
        self.info_label.config(
            text=f"{self.tr('current')}: {self.revealed} | {self.tr('alert')}: {self.alert_level}% | {self.tr('attempts')}: {self.attempts} | {self.tr('time')}: {elapsed:.1f}s | XP: {self.xp} | {self.tr('rank')}: {self.rank} | {self.tr('methods')}: {methods}"
        )

    def process_command(self, _event=None):
        raw_cmd = self.cmd_entry.get().strip()
        cmd = raw_cmd.lower()
        self.cmd_entry.delete(0, tk.END)
        if not cmd:
            return
        self.log_msg(f"> {raw_cmd}")
        if self.game_over and cmd not in {"menu", "clear", "status", "help", "commands"}:
            self.log_msg("Mission is already closed. Start a new mission or return to menu.")
            return

        handled = True
        if cmd in {"help", "commands"}:
            self.show_help_commands()
        elif cmd in {"profile", "scan profile"}:
            self.show_profile()
        elif cmd in {"scan leaks", "leaks"}:
            self.scan_leaks()
        elif cmd in {"hint", "clue", "nyom"}:
            self.show_next_clue()
        elif cmd == "hash" or cmd == "scan hash":
            self.show_hash_status()
        elif cmd == "shop":
            self.show_shop()
        elif cmd.startswith("buy "):
            self.buy_item(cmd.split(" ", 1)[1])
        elif cmd == "inventory":
            self.show_inventory()
        elif cmd == "predict":
            self.pattern_predict()
        elif cmd.startswith("attack "):
            self.use_attack(cmd.split(" ", 1)[1])
        elif cmd.startswith("submit "):
            self.submit_password(raw_cmd[7:].strip())
        elif cmd.startswith("build "):
            self.build_password(raw_cmd[6:].strip())
        elif cmd == "puzzle":
            self.start_puzzle()
        elif cmd.startswith("puzzle "):
            self.submit_puzzle_answer(raw_cmd.split(" ", 2))
        elif cmd.startswith("decode "):
            self.decode_command(raw_cmd.split(" ", 2))
        elif cmd == "trace target" or cmd == "trace":
            self.trace_target()
        elif cmd == "boss":
            self.run_boss_phase()
        elif cmd.startswith("difficulty "):
            self.set_difficulty(cmd.split(" ", 1)[1])
        elif cmd == "status":
            self.show_status()
        elif cmd == "stats":
            self.show_player_stats()
        elif cmd == "clear":
            self.log.delete("1.0", tk.END)
        elif cmd == "menu":
            self.show_main_menu()
        else:
            handled = False
            self.log_msg("[-] Unknown command. Type help.", sound="fail")

        if handled and not self.game_over and cmd not in {"help", "commands", "clear", "menu"}:
            self.maybe_random_event()
        self.update_info_label()

    def show_profile(self):
        self.log_msg("[PROFILE CACHE]")
        lines = self.current_target["profile"] if "social_scraper" in self.inventory else self.current_target["profile"][:2]
        for line in lines:
            self.log_msg(f" - {line}")
        if "social_scraper" not in self.inventory:
            self.log_msg("Tip: social_scraper reveals the full profile cache.")
        self.raise_alert(3)

    def scan_leaks(self):
        self.log_msg("[LEAK SCANNER]")
        for line in self.current_target["leaks"]:
            self.log_msg(f" - {line}")
        self.raise_alert(4 if "metadata_scanner" in self.inventory else 9)

    def show_next_clue(self):
        clues = self.current_target["profile"] + self.current_target["leaks"]
        if self.clues_seen >= len(clues):
            self.log_msg("[CLUE] No more cached clues.")
            return
        self.used_hint = True
        self.log_msg(f"[CLUE {self.clues_seen + 1}] {clues[self.clues_seen]}")
        self.clues_seen += 1
        self.raise_alert(6)

    def show_hash_status(self):
        md5_hash, sha_hash = self.get_hashes(self.password)
        self.log_msg("MD5     : " + md5_hash)
        self.log_msg("SHA256  : " + sha_hash)
        self.log_msg("STATUS  : CRACKING...")
        if "hash_analyzer" in self.inventory:
            self.reveal_some_letters(1)
            self.log_msg("[HASH ANALYZER] One character recovered.", sound="success")
        self.raise_alert(4)

    def build_password(self, expression):
        if not expression:
            self.log_msg("Usage: build <part> <part> ...")
            return
        values = []
        for token in expression.replace("+", " ").split():
            key = token.strip().lower()
            values.append(self.current_target["parts"].get(key, token))
        candidate = "".join(values)
        self.log_msg(f"[BUILDER] Candidate: {candidate}")
        if candidate == self.password:
            self.log_msg("[BUILDER] Pattern solved. Submitting candidate...", sound="success")
            self.submit_password(candidate)
        else:
            self.raise_alert(5)
            self.log_msg("[BUILDER] Pattern mismatch.", sound="fail")

    def pattern_predict(self):
        if "pattern_predictor" not in self.inventory:
            self.log_msg("Pattern predictor is not installed. Buy it in the black market.", sound="fail")
            return
        self.log_msg(f"[PREDICTOR] Most likely structure: {self.current_target['pattern']}")
        self.log_msg("[PREDICTOR] Known parts: " + ", ".join(self.current_target["parts"].keys()))
        self.reveal_some_letters(1)
        self.raise_alert(2)

    def use_attack(self, method):
        aliases = {
            "dict": "dictionary",
            "dictionary": "dictionary",
            "john": "john",
            "ripper": "john",
            "hydra": "hydra",
            "mask": "mask",
            "brute": "mask",
            "bruteforce": "mask",
            "ghost": "ghost",
        }
        normalized = aliases.get(method.strip().lower(), method.strip().lower())
        if normalized not in self.unlocked_methods:
            self.log_msg(f"[-] Method locked: {normalized}. Gain XP to unlock it.", sound="alarm")
            self.raise_alert(8)
            return

        self.stats["favorite_attack"][normalized] = self.stats["favorite_attack"].get(normalized, 0) + 1
        self.attempts += 1
        self.log_msg(f"[ATTACK] Running {normalized} module...")
        chance = {"dictionary": 0.25, "john": 0.35, "hydra": 0.45, "mask": 0.55, "ghost": 0.75}.get(normalized, 0.2)
        chance += {"easy": 0.1, "normal": 0, "hard": -0.08}.get(self.difficulty, 0)
        if random.random() < chance:
            self.reveal_some_letters(max(1, len(self.password) // 3))
            self.add_xp(12)
            self.log_msg("[+] Pattern fragment recovered.", sound="success")
            self.raise_alert(5)
        else:
            self.log_msg("[-] Attack failed. Noise detected.", sound="fail")
            self.raise_alert(13)

    def reveal_some_letters(self, count):
        revealed = list(self.revealed)
        hidden_indexes = [idx for idx, char in enumerate(revealed) if char == "_"]
        random.shuffle(hidden_indexes)
        for idx in hidden_indexes[:count]:
            revealed[idx] = self.password[idx]
        self.revealed = "".join(revealed)
        if "_" not in self.revealed:
            self.log_msg("[+] Full password reconstructed. Use submit to confirm.")

    def submit_password(self, guess):
        self.attempts += 1
        if guess == self.password:
            if self.current_target == self.boss_target and self.boss_phase < len(self.current_target["boss_phases"]):
                self.log_msg("[LOCKED] Boss chain is not complete. Use boss.", sound="alarm")
                self.raise_alert(10)
                return
            self.log_msg("[ACCESS GRANTED] Password accepted.", sound="access")
            self.finish_game(True)
            return
        self.log_msg("[ACCESS DENIED] Wrong password.", sound="alarm")
        self.raise_alert(14)

    def start_puzzle(self):
        self.active_puzzle = random.choice(self.puzzles)
        self.log_msg(f"[PUZZLE] {self.active_puzzle['title']}")
        self.log_msg(self.active_puzzle["question"])
        self.log_msg(f"Submit with: puzzle {self.active_puzzle['type']} <answer>")
        answer = simpledialog.askstring(self.active_puzzle["title"], self.active_puzzle["question"])
        if answer:
            self.check_puzzle(self.active_puzzle["type"], answer)

    def submit_puzzle_answer(self, parts):
        if len(parts) < 3:
            self.log_msg("Usage: puzzle <type> <answer>")
            return
        self.check_puzzle(parts[1].lower(), parts[2].strip())

    def check_puzzle(self, puzzle_type, answer):
        puzzle = next((item for item in self.puzzles if item["type"] == puzzle_type), None)
        if not puzzle:
            self.log_msg("Unknown puzzle type.", sound="fail")
            return
        if answer.strip().lower() == puzzle["answer"].lower():
            self.log_msg("[PUZZLE SOLVED] Intelligence fragment unlocked.", sound="success")
            self.stats["puzzles_solved"] += 1
            self.reveal_some_letters(2)
            self.add_xp(puzzle["reward"])
            self.raise_alert(2)
            return
        self.log_msg("[PUZZLE FAILED] Incorrect answer.", sound="fail")
        self.raise_alert(11)

    def run_boss_phase(self):
        if self.current_target != self.boss_target:
            self.log_msg("No boss chain in this mission.")
            return
        phases = self.current_target["boss_phases"]
        if self.boss_phase >= len(phases):
            self.log_msg("[BOSS] Chain already complete. Submit or build the final password.")
            return
        puzzle_type = phases[self.boss_phase]
        puzzle = next(item for item in self.puzzles if item["type"] == puzzle_type)
        self.log_msg(f"[BOSS PHASE {self.boss_phase + 1}/{len(phases)}] {puzzle['title']}")
        self.log_msg(puzzle["question"])
        answer = simpledialog.askstring("Boss Phase", puzzle["question"])
        if answer and answer.strip().lower() == puzzle["answer"].lower():
            self.boss_phase += 1
            self.stats["puzzles_solved"] += 1
            self.log_msg("[BOSS] Phase cleared.", sound="success")
            self.reveal_some_letters(2)
            self.add_xp(35)
            if self.boss_phase >= len(phases):
                self.log_msg("[BOSS] All phases cleared. Final password can be submitted.", sound="access")
        else:
            self.log_msg("[BOSS] Phase failed.", sound="alarm")
            self.raise_alert(15)

    def decode_command(self, parts):
        if len(parts) < 3:
            self.log_msg("Usage: decode <base64|caesar|morse> <text>")
            return
        mode = parts[1].lower()
        text = parts[2]
        try:
            if mode == "base64":
                result = base64.b64decode(text).decode("utf-8")
            elif mode == "caesar":
                result = self.caesar_decode(text, 3)
            elif mode == "morse":
                result = self.morse_decode(text)
            else:
                self.log_msg("Unknown decoder. Use base64, caesar, or morse.")
                return
            self.log_msg(f"[DECODE] {result}")
        except Exception:
            self.log_msg("[DECODE] Could not decode input.", sound="fail")

    def caesar_decode(self, text, shift):
        output = []
        for char in text:
            if "a" <= char <= "z":
                output.append(chr((ord(char) - ord("a") - shift) % 26 + ord("a")))
            elif "A" <= char <= "Z":
                output.append(chr((ord(char) - ord("A") - shift) % 26 + ord("A")))
            else:
                output.append(char)
        return "".join(output)

    def morse_decode(self, text):
        table = {
            ".-": "A", "-...": "B", "-.-.": "C", "-..": "D", ".": "E", "..-.": "F",
            "--.": "G", "....": "H", "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
            "--": "M", "-.": "N", "---": "O", ".--.": "P", "--.-": "Q", ".-.": "R",
            "...": "S", "-": "T", "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
            "-.--": "Y", "--..": "Z",
        }
        return "".join(table.get(part, "?") for part in text.split())

    def trace_target(self):
        outcomes = [
            ("Proxy route stable. Alert reduced.", -8),
            ("Trace bounced through old VPN endpoint. New leak found.", 4),
            ("Counter-trace detected.", 12),
        ]
        message, alert = random.choice(outcomes)
        self.log_msg(f"[TRACE] {message}")
        if "New leak" in message:
            self.scan_leaks()
        self.raise_alert(alert)

    def maybe_random_event(self):
        chance = {"easy": 0.08, "normal": 0.14, "hard": 0.22}.get(self.difficulty, 0.14)
        if random.random() > chance:
            return
        events = [
            ("Firewall spike detected.", 12),
            ("Proxy unstable. Route noise rising.", 8),
            ("New leak discovered in paste cache.", -2),
            ("Trace attempt blocked by shield.", 5),
        ]
        message, alert = random.choice(events)
        if "proxy_shield" in self.inventory and alert > 0:
            alert = max(1, alert // 2)
        self.log_msg(f"[EVENT] {message}")
        if "New leak" in message:
            self.reveal_some_letters(1)
        self.raise_alert(alert)

    def raise_alert(self, amount):
        self.alert_level = max(0, min(100, self.alert_level + amount))
        if self.alert_level >= 100:
            self.log_msg("[ALERT 100%] Trace completed. Mission burned.", sound="alarm")
            self.finish_game(False)

    def show_status(self):
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.log_msg(f"Target  : {self.current_target['name']}")
        self.log_msg(f"Pattern : {self.current_target['pattern']}")
        self.log_msg(f"Current : {self.revealed}")
        self.log_msg(f"Alert   : {self.alert_level}%")
        self.log_msg(f"Time    : {elapsed:.1f}s")

    def finish_game(self, success):
        self.game_over = True
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.score = max(0, 16000 - self.attempts * 450 - int(elapsed * 70) - self.clues_seen * 150 - self.alert_level * 35)
        if not success:
            messagebox.showwarning("Game Over", f"The password was: {self.password}")
            return

        earned_xp = 55 + max(0, 30 - self.attempts * 3)
        if elapsed < 20:
            earned_xp += 30
        if not self.used_hint:
            earned_xp += 40
        if self.current_target == self.boss_target:
            earned_xp += 120
            self.stats["campaign_completed"] += 1
            self.campaign_index = 0
        elif self.campaign_mode:
            self.campaign_index += 1

        self.stats["missions_completed"] += 1
        self.stats["total_time"] = round(float(self.stats["total_time"]) + elapsed, 2)
        self.stats["best_score"] = max(int(self.stats["best_score"]), self.score)
        self.add_xp(earned_xp)
        new_achievements = self.check_achievements(elapsed)
        self.save_highscore(elapsed)
        self.save_progress()

        win = tk.Toplevel(self.root)
        win.title("MISSION COMPLETE")
        win.geometry("760x560")
        win.configure(bg="#000000")
        tk.Label(win, text="MISSION COMPLETE", font=("Courier", 26, "bold"), fg=self.text_color, bg="#000000").pack(pady=22)
        tk.Label(win, text=f"Target: {self.current_target['name']}", font=("Courier", 14), fg=self.warning_color, bg="#000000").pack()
        tk.Label(win, text=f"Password: {self.password}", font=("Courier", 14), fg=self.warning_color, bg="#000000").pack(pady=7)
        tk.Label(win, text=f"Score: {self.score} | Time: {elapsed:.1f}s | Alert: {self.alert_level}% | XP: {self.xp} | Rank: {self.rank}",
                 font=("Courier", 12), fg=self.warning_color, bg="#000000").pack(pady=7)

        if new_achievements:
            tk.Label(win, text="NEW ACHIEVEMENTS", font=("Courier", 14, "bold"), fg="#ff66cc", bg="#000000").pack(pady=14)
            for item in new_achievements:
                tk.Label(win, text=item, font=("Courier", 12), fg="#ffffff", bg="#000000").pack()

        button_frame = tk.Frame(win, bg="#000000")
        button_frame.pack(pady=30)
        tk.Button(button_frame, text="NEXT CAMPAIGN", font=("Courier", 13, "bold"), bg="#b00020", fg="white", width=18,
                  command=lambda: [win.destroy(), self.start_mission(True)]).pack(side=tk.LEFT, padx=8)
        tk.Button(button_frame, text="RANDOM", font=("Courier", 13, "bold"), bg="#147a32", fg="white", width=14,
                  command=lambda: [win.destroy(), self.start_mission(False)]).pack(side=tk.LEFT, padx=8)
        tk.Button(button_frame, text="MENU", font=("Courier", 13, "bold"), bg="#0066aa", fg="white", width=14,
                  command=lambda: [win.destroy(), self.show_main_menu()]).pack(side=tk.LEFT, padx=8)

    def check_achievements(self, elapsed):
        checks = []
        if not self.used_hint:
            checks.append("No Hint Hero")
        if elapsed < 20:
            checks.append("Under 20 Seconds")
        if self.attempts == 1:
            checks.append("Perfect Run")
        if self.rank == "Ghost":
            checks.append("Ghost Operator")
        if self.rank in {"Elite", "Ghost"}:
            checks.append("Elite Cracker")
        if self.current_target == self.boss_target:
            checks.append("Architect Down")
        if self.alert_level <= 15:
            checks.append("Silent Trace")

        new_items = [item for item in checks if item not in self.unlocked_achievements]
        if new_items:
            self.unlocked_achievements.extend(new_items)
            self.save_json(ACHIEVEMENT_FILE, self.unlocked_achievements)
        return new_items

    def save_highscore(self, elapsed):
        entry = {
            "target": self.current_target["name"],
            "score": self.score,
            "attempts": self.attempts,
            "time": round(elapsed, 2),
            "rank": self.rank,
            "difficulty": self.difficulty,
        }
        self.highscores.append(entry)
        self.highscores = sorted(self.highscores, key=lambda item: item.get("score", 0), reverse=True)[:10]
        self.save_json(HIGHSCORE_FILE, self.highscores)

    def show_shop(self):
        win = tk.Toplevel(self.root)
        win.title("Black Market")
        win.geometry("760x520")
        win.configure(bg="#000000")
        text = scrolledtext.ScrolledText(win, bg="#000000", fg=self.text_color, font=("Courier", 11))
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text.insert(tk.END, f"BLACK MARKET | XP: {self.xp}\n\n")
        for name, item in self.shop_items.items():
            status = "OWNED" if name in self.inventory else f"{item['cost']} XP"
            text.insert(tk.END, f"{name:18} {status:10} {item['desc']}\n")
        text.insert(tk.END, "\nUse command in mission: buy <item_name>\n")

    def buy_item(self, item_name):
        item_name = item_name.strip().lower()
        if item_name not in self.shop_items:
            self.log_msg("Unknown market item.", sound="fail")
            return
        if item_name in self.inventory:
            self.log_msg("Item already installed.")
            return
        cost = self.shop_items[item_name]["cost"]
        if self.xp < cost:
            self.log_msg(f"Not enough XP. Need {cost} XP.", sound="fail")
            return
        self.xp -= cost
        self.inventory.add(item_name)
        self.save_progress()
        self.log_msg(f"[MARKET] Installed {item_name}.", sound="success")

    def show_inventory(self):
        if not self.inventory:
            self.log_msg("[INVENTORY] Empty.")
            return
        self.log_msg("[INVENTORY] " + ", ".join(sorted(self.inventory)))

    def set_difficulty(self, value):
        if value not in {"easy", "normal", "hard"}:
            self.log_msg("Difficulty options: easy, normal, hard")
            return
        self.difficulty = value
        self.save_progress()
        self.log_msg(f"Difficulty set to {self.difficulty}.")

    def show_player_stats(self):
        win = tk.Toplevel(self.root)
        win.title("Player Stats")
        win.geometry("640x460")
        win.configure(bg="#000000")
        text = scrolledtext.ScrolledText(win, bg="#000000", fg=self.text_color, font=("Courier", 11))
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        favorite = "N/A"
        if self.stats["favorite_attack"]:
            favorite = max(self.stats["favorite_attack"], key=self.stats["favorite_attack"].get)
        text.insert(tk.END, f"PLAYER PROFILE\n\n")
        text.insert(tk.END, f"Rank               : {self.rank}\n")
        text.insert(tk.END, f"XP                 : {self.xp}\n")
        text.insert(tk.END, f"Missions completed : {self.stats['missions_completed']}\n")
        text.insert(tk.END, f"Campaign completed : {self.stats['campaign_completed']}\n")
        text.insert(tk.END, f"Puzzles solved     : {self.stats['puzzles_solved']}\n")
        text.insert(tk.END, f"Best score         : {self.stats['best_score']}\n")
        text.insert(tk.END, f"Total time         : {self.stats['total_time']}s\n")
        text.insert(tk.END, f"Favorite attack    : {favorite}\n")
        text.insert(tk.END, f"Inventory          : {', '.join(sorted(self.inventory)) or 'empty'}\n")

    def show_highscores(self):
        win = tk.Toplevel(self.root)
        win.title("High Scores")
        win.geometry("800x500")
        win.configure(bg="#000000")
        text = scrolledtext.ScrolledText(win, bg="#000000", fg=self.text_color, font=("Courier", 11))
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        if not self.highscores:
            text.insert(tk.END, "No high scores yet.\n")
            return
        for index, item in enumerate(self.highscores, 1):
            target = item.get("target", "N/A")
            score = int(item.get("score", 0))
            elapsed = float(item.get("time", 0))
            rank = item.get("rank", item.get("level", "N/A"))
            difficulty = item.get("difficulty", "normal")
            text.insert(tk.END, f"{index:2d}. {target:16} Score: {score:5d} | {elapsed:5.1f}s | {rank:12} | {difficulty}\n")

    def show_achievements(self):
        win = tk.Toplevel(self.root)
        win.title("Achievements")
        win.geometry("560x470")
        win.configure(bg="#000000")
        all_achievements = ["No Hint Hero", "Under 20 Seconds", "Perfect Run", "Ghost Operator", "Elite Cracker", "Architect Down", "Silent Trace"]
        tk.Label(win, text="ACHIEVEMENTS", font=("Courier", 18, "bold"), fg=self.text_color, bg="#000000").pack(pady=18)
        for item in all_achievements:
            status = "UNLOCKED" if item in self.unlocked_achievements else "LOCKED"
            color = self.warning_color if status == "UNLOCKED" else "#666666"
            tk.Label(win, text=f"{status:8}  {item}", font=("Courier", 12), fg=color, bg="#000000").pack(anchor="w", padx=45, pady=5)

    def show_help_commands(self):
        win = tk.Toplevel(self.root)
        win.title(self.tr("help_commands"))
        win.geometry("980x760")
        win.configure(bg="#0a0a0a")
        text = scrolledtext.ScrolledText(win, bg="#000000", fg=self.text_color, font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        if self.language == "hu":
            content = """CTF JELSZOTORES - PARANCSOK

scan profile            Celpont profil adatok
scan leaks              Kiszivargott jegyzetek keresese
clue / hint / nyom      Egy nyom felfedese
hash / scan hash        MD5/SHA256 panel
predict                 Pattern predictor hasznalata
build <reszek>          Jelszo osszerakasa kulcsokbol vagy ertekekbol
attack dictionary       Alap tamadas, kezdetektol elerheto
attack john             100 XP utan oldodik fel
attack hydra            180 XP utan oldodik fel
attack mask             250 XP utan oldodik fel
attack ghost            500 XP utan oldodik fel
puzzle                  CTF feladat inditasa
puzzle <tipus> <valasz> CTF valasz bekuldese
decode base64 <text>    Base64 dekodolas
decode caesar <text>    Caesar -3 dekodolas
decode morse <text>     Morse kod dekodolas
trace target            Nyomkovetes kezelese
boss                    Kovetkezo boss fazis
shop                    Fekete piac
buy <item>              Eszkoz vasarlasa XP-bol
inventory               Telepitett eszkozok
difficulty easy|normal|hard
submit <password>       Vegso jelszo bekuldese
status                  Kuldetes allapota
stats                   Jatekos profil
clear                   Terminal torlese
menu                    Vissza a menube

Rangok: Script Kiddie -> Hacker -> Elite -> Ghost
A kampany vegso ellenfele: The Architect.
"""
        else:
            content = """CTF PASSWORD CRACKING - COMMANDS

scan profile            Show target profile data
scan leaks              Search leaked notes
clue / hint / nyom      Reveal one clue line
hash / scan hash        Show MD5/SHA256 cracking panel
predict                 Use pattern_predictor if installed
build <parts>           Build password from keys or literal values
attack dictionary       Basic attack, unlocked from start
attack john             Unlocks at 100 XP
attack hydra            Unlocks at 180 XP
attack mask             Unlocks at 250 XP
attack ghost            Unlocks at 500 XP
puzzle                  Start a CTF puzzle
puzzle <type> <answer>  Submit puzzle answer
decode base64 <text>    Decode Base64
decode caesar <text>    Decode Caesar -3
decode morse <text>     Decode Morse code
trace target            Try to reduce or manage trace risk
boss                    Run next boss phase
shop                    Show black market
buy <item>              Buy item with XP
inventory               Show installed tools
difficulty easy|normal|hard
submit <password>       Submit final password
status                  Show mission status
stats                   Show player profile
clear                   Clear terminal
menu                    Back to main menu

Ranks: Script Kiddie -> Hacker -> Elite -> Ghost
Campaign ends with The Architect boss chain.
"""
        text.insert(tk.END, content)

    def open_settings(self):
        win = tk.Toplevel(self.root)
        win.title(self.tr("settings"))
        win.geometry("420x420")
        win.configure(bg="#1a1a1a")
        tk.Label(win, text=self.tr("settings"), font=("Courier", 16, "bold"), fg=self.text_color, bg="#1a1a1a").pack(pady=18)
        tk.Label(win, text=self.tr("language"), font=("Courier", 12, "bold"), fg=self.warning_color, bg="#1a1a1a").pack(pady=(4, 6))
        tk.Button(win, text=self.tr("hungarian"), bg="#147a32" if self.language == "hu" else "#444444", fg="white", command=lambda: [win.destroy(), self.set_language("hu")]).pack(pady=4, fill="x", padx=40)
        tk.Button(win, text=self.tr("english"), bg="#147a32" if self.language == "en" else "#444444", fg="white", command=lambda: [win.destroy(), self.set_language("en")]).pack(pady=4, fill="x", padx=40)
        tk.Button(win, text=self.tr("background_color"), bg="#444444", fg="white", command=self.choose_bg_color).pack(pady=8, fill="x", padx=40)
        tk.Button(win, text=self.tr("text_color"), bg="#444444", fg="white", command=self.choose_text_color).pack(pady=8, fill="x", padx=40)
        tk.Button(win, text=self.tr("difficulty_easy"), bg="#147a32", fg="white", command=lambda: self.set_menu_difficulty("easy")).pack(pady=5, fill="x", padx=40)
        tk.Button(win, text=self.tr("difficulty_normal"), bg="#0066aa", fg="white", command=lambda: self.set_menu_difficulty("normal")).pack(pady=5, fill="x", padx=40)
        tk.Button(win, text=self.tr("difficulty_hard"), bg="#b00020", fg="white", command=lambda: self.set_menu_difficulty("hard")).pack(pady=5, fill="x", padx=40)
        tk.Button(win, text=self.tr("reset_colors"), bg="#666666", fg="white", command=self.reset_colors).pack(pady=12, fill="x", padx=40)

    def set_menu_difficulty(self, value):
        self.difficulty = value
        self.save_progress()
        self.show_main_menu()

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose background color")[1]
        if color:
            self.bg_color = color
            self.show_main_menu()

    def choose_text_color(self):
        color = colorchooser.askcolor(title="Choose text color")[1]
        if color:
            self.text_color = color
            self.show_main_menu()

    def reset_colors(self):
        self.bg_color = "#070707"
        self.text_color = "#00ff41"
        self.show_main_menu()

    def toggle_fullscreen(self, state=None):
        self.fullscreen = not self.fullscreen if state is None else state
        self.root.attributes("-fullscreen", self.fullscreen)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CTFPasswordCracker()
    app.run()
