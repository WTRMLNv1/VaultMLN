# VaultMLN
A Melogne Studio project.
<p align="left">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/studio-badge.svg" height="40">
</p>
<p align="left">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/OS-badge.svg" height="30">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/version-badge.svg" height="30">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/license-badge.svg" height="30">
</p>

<<<<<<< Updated upstream
A [Melogne Studio](https://github.com/MelogneStudio?utm_source=chatgpt.com) project.

<p align="left">
  <a href="https://github.com/MelogneStudio">
    <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/TrackMLN-assets/badges/studio-badge.svg" height="40">
  </a>
</p>

<p align="left">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/version-badge.svg" height="30">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/license-badge.svg" height="30">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/ui-badge.svg" height="30">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/builtwith-badge.svg" height="30">
</p>

VaultMLN is a lightweight Windows password vault focused on simplicity, local-first storage, and a clean desktop UI.

Built as an early Melogne Studio project, VaultMLN was designed to be fast, minimal, and easy to use without cloud accounts, subscriptions, or unnecessary complexity.

> ℹ️ Windows only.
> (because i was NOT about to debug cross-platform CustomTkinter issues at 2am)

---

## Features

* Local-first encrypted password storage
* Master-password derived encryption keys
* Clean desktop UI built with CustomTkinter
* Fast add/search/delete workflows
* Multiple accounts per site support
* Custom themes and appearance settings
* Portable single-folder structure
* Lightweight and offline by default

---

## Security

VaultMLN uses:

* **PBKDF2-HMAC-SHA256** for key derivation
* **Fernet encryption** for vault data
* Local salt generation and management
* Master-password based encryption keys

Your master password is never stored.

All vault data stays inside the local `Data` folder on your machine.

---

## How To Download

Grab the latest release from the Releases page:

<p align="left">
  <a href="https://github.com/WTRMLNv1/VaultMLN/releases">
    <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/TrackMLN-assets/badges/releases-page.svg" height="30">
  </a>
</p>

Or download directly:

<p align="left">
  <a href="https://github.com/WTRMLNv1/VaultMLN/releases/download/v1.1/VaultMLN.exe">
    <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/TrackMLN-assets/badges/download_button.svg" height="30">
  </a>
</p>

---

## What's New — v1.1

* Added custom themes and appearance settings
* Improved Check Site search speed and formatting
* Added multi-entry support for the same site
* Added duplicate-entry detection and replace confirmation
* Redesigned Delete Site screen and delete confirmation flow
* Improved overall UI consistency and usability

---

## Screenshots

### Main UI

<p align="center">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/home_page.png" width="45%" />
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/enter_password.png" width="45%" />
</p>

---

### Vault Management

<p align="center">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/add_password.png" width="45%" />
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/check_password.png" width="45%" />
</p>

---

### Settings & Deletion

<p align="center">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/delete_password.png" width="45%" />
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/settings.png" width="45%" />
</p>

---

## Quick Start

### Requirements

* Python 3.10+
* `cryptography`
* `customtkinter`

Install dependencies:
=======
<p align="left">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/backend-badge.svg" height="30">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/framework-badge.svg" height="30">
  <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/ui-badge.svg" height="30">
</p>

VaultMLN is a local password manager. No cloud, no accounts, no breach notification emails. Just AES-256-GCM, your master password, and a Tauri app that actually looks good.

> ℹ️ Windows only. (Yes, again.)

### ⚠️ Common "bugs" for people who skip the readme

1. **v1 vaults don't carry over.** v2.0 is a full rewrite — old Python/Fernet entries are not compatible with the new Rust/AES-GCM backend. There's no auto-migration. Extract your old data manually from the legacy Python files if you need it.
2. **SmartScreen will yell at you.** Click `More info` → `Run anyway`. The app isn't code-signed. It costs money. I don't have that money.

## What It Does

- Multi-account vault architecture — each account has its own salt, verifier hash, and completely isolated data
- AES-256-GCM encryption with per-field nonces
- PBKDF2-HMAC-SHA256 key derivation — 390,000 iterations
- Master password is never stored. If you forget it, the vault is gone. Back it up.
- Full account lifecycle: create, unlock, switch, change master password (with full re-encryption), delete
- Add, view, replace, and delete password entries per account
- Clipboard copy support
- Accent color picker, because aesthetics matter
- Comes with a custom installer so you don't have to deal with any of that yourself

## How to Download

Just want it? Click the download button.

Or grab it from the Releases page — look for `vaultmln-installer-v2.x.x.exe` in the Assets section.

<p align="left">
  <a href="https://github.com/WTRMLNv1/VaultMLN/releases">
    <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/download_button.svg" height="30">
  </a>
</p>

<p align="left">
  <a href="https://github.com/WTRMLNv1/VaultMLN/releases">
    <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/releases-page.svg" height="30">
  </a>
</p>

After downloading:

1. Run the installer
2. If Windows SmartScreen appears, click `More info` → `Run anyway`
   *(The app isn't code-signed yet — this is expected)*
3. Finish setup

The installer will:
- install VaultMLN into your local app data folder
- create a Start Menu shortcut
- optionally create a Desktop shortcut

## What's New

### v2.0.0 — Tauri + Rust Rebuild

Python is gone. The whole thing got rebuilt from scratch.

**Backend**
- Migrated from Python + CustomTkinter to Tauri 2 + React + Rust
- Replaced Fernet/OpenSSL with a pure Rust crypto stack: `aes-gcm`, `pbkdf2`, `hmac`, `sha2`, `rand`
- AES-256-GCM encryption for all vault data
- PBKDF2-HMAC-SHA256 key derivation with 390,000 iterations
- Per-field nonce storage for AES-GCM
- Zero OpenSSL, zero vcpkg, zero Perl *(yes the old build needed Perl, we don't talk about it)*

**Accounts**
- Full account-based vault architecture replacing the old single-vault setup
- Per-account salts and verifier hashes
- Account switching, deletion, master password change with re-encryption

**Frontend**
- Full React + Vite UI redesign
- Dark compact shell: sidebar, topbar, stat cards, action cards
- Searchable list + detail panel for vault entries
- Accent color picker
- Clipboard copy via Tauri clipboard plugin

**Installer**
- Separate custom Tauri installer under `installer/`
- Install location, desktop shortcut, Start Menu shortcut options
- Launch-after-install support
- Uninstall registry entry

### v1.1.0
- Custom themes and appearance settings
- Improved Check Site screen with faster search and `{site} | {username}` display for multi-account entries
- Multi-entry support per site (different usernames allowed, duplicate prompts on exact match)
- Redesigned Delete Site screen

### v1.0.0
- Initial release

## Screenshots

*(screenshots go here when you take them)*

## Migration from v1

Old Python Fernet vault entries are **not compatible** with the new Rust/AES-GCM backend. The old Python source files are still in the repo — use them to manually extract your old data if you need it. There's no auto-migration tool.

## Tech Stack

- Tauri 2
- React 18
- TypeScript
- Vite
- Rust
- AES-256-GCM via `aes-gcm`
- PBKDF2-HMAC-SHA256 via `pbkdf2` + `hmac` + `sha2`
>>>>>>> Stashed changes

## Project Structure

```text
.
├─ src/                 React frontend
├─ src-tauri/           Rust backend + Tauri config
├─ installer/           Separate Tauri app that installs VaultMLN
│  ├─ src/              Installer frontend
│  └─ src-tauri/        Installer backend
```

## How the Crypto Works

Each account gets its own random salt on creation. Your master password is run through PBKDF2-HMAC-SHA256 (390,000 iterations) to derive the encryption key. A separate verifier hash is stored to validate your password on unlock without decrypting anything.

<<<<<<< Updated upstream
---

## Typical Workflow

* Launch the app
* Enter your master password
* Add new entries
* Search saved accounts
* Delete individual or grouped entries
* Customize themes and settings

VaultMLN supports multiple accounts for the same site as long as usernames differ.

---

## Important Files

```text
.
├─ Functions/
│  ├─ encrypt.py
│  ├─ kdf.py
│  ├─ manager.py
│  ├─ themeManager.py
│  └─ salt.py
│
├─ ui/
│  ├─ add_password.py
│  ├─ checkSite.py
│  ├─ deletePassword.py
│  └─ settingsScreen.py
│
├─ Data/
│  ├─ salt.bin
│  └─ vault data
│
└─ main.py
```

---

## Security Notes

* Salt is stored locally in `Data/salt.bin`
* Encryption keys are derived from the master password
* VaultMLN does not use cloud sync
* Your data never leaves your machine
* Back up your `Data` folder if you want to migrate your vault

---

## Current Status

VaultMLN is considered complete and archived.

TrackMLN became the primary active Melogne Studio project afterward, but VaultMLN remains fully functional and available.

---

## Development

Run normally:

```bash
python main.py
```

Generate the legacy key file manually if needed:
=======
Every encrypted field — username, password — gets its own AES-GCM nonce. Nothing is shared, nothing is reused.

The master password never touches disk. If you lose it, there is no recovery.

## Current Scope

VaultMLN is intentionally local and simple.

- All data stays on your machine — no accounts, no cloud, no sync
- Windows-only because I don't have anything else to test on
- The old Python source is still in the repo as legacy reference, not active code

## Known Bugs

Nothing major found in v2.0.0 yet. If something explodes, please open an issue. :')

<p align="left">
  <a href="https://github.com/WTRMLNv1/VaultMLN/issues">
    <img src="https://raw.githubusercontent.com/WTRMLNv1/WTRMLNv1/main/VaultMLN-assets/badges/report-a-bug.svg" height="30">
  </a>
</p>

## Local Data

VaultMLN stores everything in the Tauri app data directory:

- `vault.json` — encrypted vault entries scoped per account
- Account salts and verifier hashes stored separately per account

## Planned

- Auto-fill / browser integration (maybe, one day, if I feel like it)
- Password generator UI
- Import/export

## Known Limitations

- Windows-only (will make macOS if you buy me a MacBook to test it on ;))
- No cloud sync, by design
- No migration tool from v1 — manual extraction only

## Development

### Requirements
>>>>>>> Stashed changes

- Windows
- Node.js + npm
- Rust toolchain
- Tauri prerequisites for Windows

### Install dependencies

```powershell
npm install
```

<<<<<<< Updated upstream
---
=======
### Run in dev mode
>>>>>>> Stashed changes

```powershell
npm run tauri dev
```

<<<<<<< Updated upstream
Contributions, fixes, and improvements are welcome.

If you're making security-sensitive changes, keep PRs focused and easy to review.

---

## License

MIT License.

Free to use, modify, and learn from.

---

Made with 💚, Debugged with 😭 by [WTRMLN](https://github.com/WTRMLNv1)
=======
### Build a release binary

```powershell
npm run tauri build
```

## Installer

The `installer/` folder is a separate Tauri app that handles installation. Build the main app first, then drop the exe into `installer/assets/app/VaultMLN.exe` before building the installer.

```powershell
# Step 1 — build the main app
npm run tauri build

# Step 2 — build the installer
cd installer
npm run tauri build
```

## License

Source-available — free for non-commercial use.
See [LICENSE](./LICENSE) for full terms.

---

Made with 💚, Debugged with 😭 by [WTRMLN](https://github.com/WTRMLNv1) @ Melogne Studio
>>>>>>> Stashed changes
© 2026 Melogne Studio
