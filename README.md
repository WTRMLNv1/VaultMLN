# VaultMLN

A minimal, secure password manager with a clean UI — fast, local, and battle-ready.

## Highlights

- Local-first storage: all vault data lives in the `Data` folder.
- Master-password derived keys: PBKDF2-HMAC-SHA256 derives a Fernet key from your master password.
- Small, focused GUI: built from the `ui` package for quick add/search/delete flows.
- Portable: single-folder project; run with Python.

## What’s new (v1.1)

- **Custom themes** — App themes and appearance settings are now supported. See [Functions/themeManager.py](Functions/themeManager.py) and the UI Settings screen ([ui/settingsScreen.py](ui/settingsScreen.py)).
- **Improved Check Site screen** — The search is faster and shows results in a clear format; when multiple entries exist for the same site the display shows entries as `{site} | {username}` so you can easily distinguish accounts.
- **Add password: multi-entry support** — You can now add multiple entries for the same site as long as they have different usernames/emails (v1.0 would silently overwrite). If you try to add an entry whose `site` and `username` both match an existing entry, a modal prompts you to either replace the existing entry or cancel.
- **New Delete Site screen** — Redesigned UI for deleting entries. Supports deleting a single entry or removing all entries for a site with confirmation modals. See [ui/deletePassword.py](ui/deletePassword.py).

## Screenshots
Screenshots in previous releases show the look-and-feel; try the app to see the new theme and list formats.

## Quick start

Latest release builds may be available in releases. To run from source:

Prerequisites:

- Python 3.10+ (3.11 recommended)
- `cryptography` and `customtkinter`

Install the dependencies:

```bash
pip install cryptography customtkinter
```

Run the app:

```bash
python main.py
```

This launches the UI and walks you through entering your master password and using the vault.

## Typical workflow

- Start with `python main.py`.
- Enter your master password (not stored) to unlock the vault.
- Use the Add screen to create new entries. The app permits multiple entries for the same site as long as usernames differ; if the site and username exactly match an existing entry you'll be prompted to replace or cancel.
- Use Check Site to search. If multiple accounts exist for a site, results are shown as `{site} | {username}`.
- Use Delete Site to remove a single account or all accounts for a site; confirmations prevent accidental loss.

## Important files

- [main.py](main.py) — application entry point.
- [Functions/encrypt.py](Functions/encrypt.py) — encryption/decryption helpers (Fernet).
- [Functions/kdf.py](Functions/kdf.py) — PBKDF2 key derivation.
- [Functions/salt.py](Functions/salt.py) — salt management; salt stored at `Data/salt.bin`.
- [Functions/generatePass.py](Functions/generatePass.py) — helper to generate a legacy `Data/secret.key` (legacy; not required normally).
- [Functions/manager.py](Functions/manager.py) — high-level password manager logic.
- [Functions/themeManager.py](Functions/themeManager.py) — theme handling and preferences.
- [ui/add_password.py](ui/add_password.py) — Add-entry screen with duplicate checks.
- [ui/checkSite.py](ui/checkSite.py) — improved search and result formatting.
- [ui/deletePassword.py](ui/deletePassword.py) — Delete screen and delete-confirm flows.
- [ui/settingsScreen.py](ui/settingsScreen.py) — theme and settings UI.

## Security notes

- Salt is created at `Data/salt.bin` and used with PBKDF2 for key derivation.
- The master password is used to derive the encryption key and is not stored.
- A legacy `Data/secret.key` file may be created by older workflows; prefer the master-password derivation.
- Keep your `Data` folder secure and back it up if you need to migrate your vault.

## Development

- To inspect how encryption works, see [Functions/encrypt.py](Functions/encrypt.py) and [Functions/kdf.py](Functions/kdf.py).
- To generate the legacy key file (not required for normal operation):

```bash
python -c "from Functions.generatePass import generate_key; generate_key()"
```

If you're working on themes, inspect [Functions/themeManager.py](Functions/themeManager.py) and [ui/settingsScreen.py](ui/settingsScreen.py).

## Contributing

Contributions welcome — open an issue or a PR. For security-sensitive changes, please keep changes small and request review.

## License

MIT Licence. Feel free to edit and modify.

Made with ❤️, Debugged with 😭 by [WTRMLN](https://github.com/WTRMLNv1)
