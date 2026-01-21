# PasswordManager

> A minimal, secure password manager with a clean UI — fast, local, and battle-ready.

## Features

- **Local-first storage:** All data is stored locally in the `Data` folder.
- **Master-password derived keys:** Uses PBKDF2-HMAC-SHA256 to derive a Fernet key from your master password.
- **Simple GUI:** Built with the `ui` package for quick add/search flows.
- **Portable:** Single-folder project; run with Python.

## Screenshots
<img width="482" height="300" alt="image" src="https://github.com/user-attachments/assets/e2a1c505-819d-43a1-97ff-79b8f772267c" />
<img width="478" height="299" alt="image" src="https://github.com/user-attachments/assets/26e8086f-4e7e-447b-ad84-2399a6eb4353" />


## Quick start

> Don't have time to download this mess? Just download the latest EXE version [here](https://github.com/WTRMLNv1/VaultMLN/releases/tag/v1.0)

Prerequisites:

- Python 3.10+ (3.11 recommended)
- `cryptography`, and `customtkinter` package

Install the dependency:

```bash install cryptography
pip install cryptography
```
```bash install customtkinter
pip install customtkinter
```
Run the app:

```bash
python main.py
```

This launches the UI, which will guide you through entering your master password and using the vault.

## Typical workflow

- Start the app with `python main.py`.
- Enter a secure master password when prompted — this password is never stored.
- Add, view, or search entries using the GUI.

## Important files

- [main.py](main.py) — application entry point.
- [Functions/encrypt.py](Functions/encrypt.py) — encryption/decryption helpers (Fernet).
- [Functions/kdf.py](Functions/kdf.py) — PBKDF2 key derivation.
- [Functions/salt.py](Functions/salt.py) — salt management; salt stored at `Data/salt.bin`.
- [Functions/generatePass.py](Functions/generatePass.py) — helper that can generate a legacy `Data/secret.key`. (Legacy - Not used in normal flow; will be removed next update)
- [Functions/manager.py](Functions/manager.py) — high-level password manager logic.
- [ui](ui) — UI screens and helpers.

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

## Contributing

Contributions welcome — open an issue or a PR. Please keep security-related changes small and reviewed.

## License

MIT Licence. Feel Free to edit and modify ;)

Made with ❤️, Debugged with 😭 by [WTRMLN](https://github.com/WTRMLNv1)
