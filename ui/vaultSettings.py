import customtkinter as ctk
from ui.helpers import create_label, divider, add_buttons, DEFAULT_FONT
from Functions.salt import load_or_create_salt
from Functions.kdf import derive_key
from cryptography.fernet import Fernet
from ui.popups import password_mismatch_alert, success_alert
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "Data" / "config.json"
PASSWORD_PATH = BASE_DIR / "Data" / "password.json"


def open_vault_settings(root, master_password: str):
    """Open a modal vault settings window. Requires `master_password` (unlocked)."""
    win = ctk.CTkToplevel(root)
    win.title("Vault Settings")
    win.geometry("420x220")
    win.transient(root)
    win.grab_set()

    ctk.CTkLabel(win, text="Vault Settings", font=("Cascadia Code", 16)).pack(pady=8)

    def change_pw():
        sub = ctk.CTkToplevel(win)
        sub.title("Change Master Password")
        sub.geometry("400x220")
        sub.transient(win)
        sub.grab_set()

        create_label(sub, text="New password:").pack(pady=(12, 4))
        n1 = ctk.CTkEntry(sub, show="*", width=300, font=DEFAULT_FONT, placeholder_text="Enter new master password")
        n1.pack()
        create_label(sub, text="Confirm new:").pack(pady=(8, 4))
        n2 = ctk.CTkEntry(sub, show="*", width=300, font=DEFAULT_FONT, placeholder_text="Confirm new master password")
        n2.pack()

        def do_change():
            new = n1.get().strip()
            newc = n2.get().strip()
            if not new or new != newc:
                password_mismatch_alert(sub)
                return
            # re-encrypt all entries
            try:
                with open(PASSWORD_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f) or {}
            except Exception:
                data = {}
            reencrypted = {}
            # decrypt with old master_password then encrypt with new
            salt = load_or_create_salt()
            old_key = derive_key(master_password, salt)
            new_key = derive_key(new, salt)
            old_f = Fernet(old_key)
            new_f = Fernet(new_key)
            for site, creds in data.items():
                try:
                    user = old_f.decrypt(creds["user"].encode()).decode()
                    pw = old_f.decrypt(creds["password"].encode()).decode()
                except Exception:
                    continue
                reencrypted[site] = {"user": new_f.encrypt(user.encode()).decode(), "password": new_f.encrypt(pw.encode()).decode()}
            PASSWORD_PATH.write_text(json.dumps(reencrypted, indent=4), encoding="utf-8")
            # update config hello
            token = new_f.encrypt(b"hello").decode()
            cfg = {}
            if CONFIG_PATH.exists():
                try:
                    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8")) or {}
                except Exception:
                    cfg = {}
            cfg["hello"] = token
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(cfg), encoding="utf-8")
            success_alert(sub, "Master password changed successfully.")
            sub.destroy()

        add_buttons(sub, text="Change Password", command=do_change).pack(pady=12)
        root.wait_window(sub)

    def wipe_all():
        # Confirm and wipe
        def do_wipe():
            PASSWORD_PATH.write_text("{}", encoding="utf-8")
            # refresh hello token so vault remains locked/unlocked
            salt = load_or_create_salt()
            token = Fernet(derive_key(master_password, salt)).encrypt(b"hello").decode()
            cfg = {}
            if CONFIG_PATH.exists():
                try:
                    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8")) or {}
                except Exception:
                    cfg = {}
            cfg["hello"] = token
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(cfg), encoding="utf-8")
            success_alert(win, "Vault wiped successfully.")
            confirm.destroy()

        confirm = ctk.CTkToplevel(win)
        confirm.title("Confirm Wipe")
        confirm.geometry("400x120")
        confirm.transient(win)
        confirm.grab_set()
        create_label(confirm, text="Existing passwords cannot be decrypted. Wipe all?").pack(pady=12)
        btnf = ctk.CTkFrame(confirm)
        btnf.pack(pady=6)
        add_buttons(btnf, text="Yes, wipe", command=do_wipe, fg_color="#b62828").pack(side="left", padx=8)
        add_buttons(btnf, text="Cancel", command=confirm.destroy).pack(side="left", padx=8)
        root.wait_window(confirm)

    add_buttons(win, text="Change Master Password", command=change_pw).pack(pady=6)
    add_buttons(win, text="Wipe All Passwords", command=wipe_all, fg_color="#b62828").pack(pady=6)
    root.wait_window(win)