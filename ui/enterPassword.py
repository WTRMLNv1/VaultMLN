# enterPassword.py
import customtkinter as ctk
from customtkinter import CENTER
from ui.helpers import create_title, create_label, add_buttons, divider, get_colors, DEFAULT_FONT
from Functions.kdf import derive_key
from Functions.salt import load_or_create_salt
from Functions import encrypt, manager
from cryptography.fernet import Fernet
from pathlib import Path
import json, os, threading, time

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "Data" / "config.json"
PASSWORD_PATH = BASE_DIR / "Data" / "password.json"
LEGACY_KEY = BASE_DIR / "Data" / "secret.key"


class EnterPasswordScreen:
    def __init__(self, ui):
        self.ui = ui
        self.colors = get_colors()
        self.frame = self.ui.frame
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.9, relheight=0.9)

        self.attempts_left = 5
        self.locked_until = 0

        self._load_config()
        self._build()

    def _load_config(self):
        if CONFIG_PATH.exists():
            try:
                self.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            except Exception:
                self.config = {}
        else:
            self.config = {}

    def _save_config(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(self.config), encoding="utf-8")

    def _has_passwords(self):
        if not PASSWORD_PATH.exists():
            return False
        try:
            data = json.loads(PASSWORD_PATH.read_text(encoding="utf-8")) or {}
            return bool(data)
        except Exception:
            return False

    def _build(self):
        create_title(self.frame, "Unlock Vault").place(relx=0.5, rely=0.08, anchor=CENTER)
        divider(self.frame).place(relx=0.5, rely=0.15, anchor=CENTER)

        if self.config.get("hello"):
            self.info_label = create_label(self.frame, "Enter master password to unlock.")
            self.info_label.place(relx=0.5, rely=0.25, anchor=CENTER)

            self.entry = ctk.CTkEntry(self.frame, show="*", font=DEFAULT_FONT, width=300)
            self.entry.place(relx=0.5, rely=0.33, anchor=CENTER)

            self.attempts_label = create_label(self.frame, f"Attempts left: {self.attempts_left}")
            self.attempts_label.place(relx=0.5, rely=0.39, anchor=CENTER)

            self.submit_btn = add_buttons(self.frame, "Submit", command=self._submit, colors_dict=self.colors)
            self.submit_btn.place(relx=0.5, rely=0.48, anchor=CENTER, relwidth=0.4)


        # If no master password configured, show create fields
        if not self.config.get("hello"):
            create_label(self.frame, "No master password set. Create one below:").place(relx=0.5, rely=0.25, anchor=CENTER)
            self.new_entry = ctk.CTkEntry(self.frame, show="*", font=DEFAULT_FONT, width=300, placeholder_text="New password")
            self.new_entry.place(relx=0.5, rely=0.33, anchor=CENTER)
            self.new_confirm = ctk.CTkEntry(self.frame, show="*", font=DEFAULT_FONT, width=300, placeholder_text="Confirm password")
            self.new_confirm.place(relx=0.5, rely=0.4, anchor=CENTER)
            self.create_btn = add_buttons(self.frame, "Create Master Password", command=self._create_master, colors_dict=self.colors)
            self.create_btn.place(relx=0.5, rely=0.5, anchor=CENTER, relwidth=0.5)

    def _submit(self):
        if time.time() < self.locked_until:
            self.info_label.configure(text=f"Locked. Try again in {int(self.locked_until - time.time())}s")
            return
        pw = self.entry.get().strip()
        if not pw:
            self.info_label.configure(text="Password required.")
            return
        # verify config hello
        if not self.config.get("hello"):
            self.info_label.configure(text="No master password configured. Create one below.")
            return
        try:
            salt = load_or_create_salt()
            key = derive_key(pw, salt)
            f = Fernet(key)
            token = self.config.get("hello")
            f.decrypt(token.encode())
        except Exception:
            self.attempts_left -= 1
            if self.attempts_left <= 0:
                self.locked_until = time.time() + 30
                self.attempts_left = 5
                self.info_label.configure(text="Too many attempts — locked for 30s")
                self.entry.configure(state="disabled")
                self.submit_btn.configure(state="disabled")
                threading.Timer(30, self._unlock).start()
            else:
                self.info_label.configure(text=f"Incorrect password. Attempts left: {self.attempts_left}")
            self.attempts_label.configure(text=f"Attempts left: {self.attempts_left}")
            return
        # success
        self.ui.master_password = pw
        self.ui.show_screen("home")

    def _unlock(self):
        self.entry.configure(state="normal")
        self.submit_btn.configure(state="normal")
        self.info_label.configure(text="Enter master password to unlock.")
        self.attempts_label.configure(text=f"Attempts left: {self.attempts_left}")

    def _create_master(self):
        a = self.new_entry.get().strip()
        b = self.new_confirm.get().strip()
        if not a:
            self.info_label.configure(text="New password required.")
            return
        if a != b:
            self.info_label.configure(text="Passwords do not match.")
            return

        # If legacy key exists and passwords present, migrate
        if LEGACY_KEY.exists() and self._has_passwords():
            try:
                # load legacy Fernet
                old_key = LEGACY_KEY.read_bytes()
                old_f = Fernet(old_key)
                data = json.loads(PASSWORD_PATH.read_text(encoding="utf-8")) or {}
                migrated = {}
                for site, creds in data.items():
                    try:
                        user = old_f.decrypt(creds["user"].encode()).decode()
                        pw = old_f.decrypt(creds["password"].encode()).decode()
                    except Exception:
                        # if any entry fails, abort migration
                        self.info_label.configure(text="Migration failed: cannot decrypt existing entries")
                        return
                    migrated[site] = {"user": encrypt.encrypt_message(user, a), "password": encrypt.encrypt_message(pw, a)}
                PASSWORD_PATH.write_text(json.dumps(migrated, indent=4), encoding="utf-8")
                # remove legacy key
                try:
                    LEGACY_KEY.unlink()
                except Exception:
                    pass
            except Exception:
                self.info_label.configure(text="Migration failed.")
                return
        else:
            # If passwords exist but no legacy key, ask user to confirm wiping
            if self._has_passwords():
                # require confirmation modal
                if not self._confirm_wipe():
                    self.info_label.configure(text="Creation cancelled — existing passwords kept.")
                    return
                # wipe
                PASSWORD_PATH.write_text("{}", encoding="utf-8")

        # store hello token
        salt = load_or_create_salt()
        token = Fernet(derive_key(a, salt)).encrypt(b"hello").decode()
        self.config["hello"] = token
        self._save_config()
        self.ui.master_password = a
        self.ui.show_screen("home")

    def _confirm_wipe(self):
        win = ctk.CTkToplevel(self.ui.root)
        win.title("Confirm Wipe")
        win.geometry("400x120")
        win.transient(self.ui.root)
        win.grab_set()
        ctk.CTkLabel(win, text="Existing passwords cannot be decrypted. Wipe all?", wraplength=360).pack(pady=12)
        res = {"ok": False}

        def yes():
            res["ok"] = True
            win.destroy()

        def no():
            win.destroy()

        btnf = ctk.CTkFrame(win)
        btnf.pack(pady=6)
        ctk.CTkButton(btnf, text="Yes, wipe", command=yes, fg_color="#b62828").pack(side="left", padx=8)
        ctk.CTkButton(btnf, text="Cancel", command=no).pack(side="left", padx=8)
        self.ui.root.wait_window(win)
        return res["ok"]
