# VaultMLN

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

```bash
pip install cryptography customtkinter
```

Run the app:

```bash
python main.py
```

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

```bash
python -c "from Functions.generatePass import generate_key; generate_key()"
```

---

## Contributing

Contributions, fixes, and improvements are welcome.

If you're making security-sensitive changes, keep PRs focused and easy to review.

---

## License

MIT License.

Free to use, modify, and learn from.

---

Made with 💚, Debugged with 😭 by [WTRMLN](https://github.com/WTRMLNv1)
© 2026 Melogne Studio
