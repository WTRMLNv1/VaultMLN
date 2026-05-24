use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use pbkdf2::pbkdf2_hmac;
use rand::{rngs::OsRng, RngCore};
use serde::{Deserialize, Serialize};
use serde_json::{json, Map, Value};
use sha2::Sha256;
use std::{
    env,
    fs,
    path::{Path, PathBuf},
};
use thiserror::Error;

const APP_NAME: &str = "VaultMLN";
const ITERATIONS: u32 = 390_000;
const TOKEN_PREFIX: &str = "vmln2.";
const NONCE_LEN: usize = 12;

#[derive(Debug, Error)]
enum VaultError {
    #[error("Master password is required.")]
    MissingMasterPassword,
    #[error("Site not found.")]
    SiteNotFound,
    #[error("No matching entry was found.")]
    EntryNotFound,
    #[error("DUPLICATE_ENTRY")]
    DuplicateEntry,
    #[error("Decryption failed. Check your master password.")]
    DecryptionFailed,
    #[error("{0}")]
    Io(String),
    #[error("{0}")]
    Data(String),
}

type VaultResult<T> = Result<T, VaultError>;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Credential {
    user: String,
    password: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct SiteDisplayItem {
    label: String,
    site: String,
    username: Option<String>,
}

impl From<VaultError> for String {
    fn from(value: VaultError) -> Self {
        value.to_string()
    }
}

fn appdata_root() -> VaultResult<PathBuf> {
    if let Ok(appdata) = env::var("APPDATA") {
        return Ok(PathBuf::from(appdata).join(APP_NAME));
    }

    let home = env::var("HOME")
        .or_else(|_| env::var("USERPROFILE"))
        .map_err(|_| VaultError::Io("Could not find the current user home directory.".into()))?;

    if cfg!(windows) {
        Ok(PathBuf::from(home).join("AppData").join("Roaming").join(APP_NAME))
    } else if let Ok(xdg) = env::var("XDG_DATA_HOME") {
        Ok(PathBuf::from(xdg).join(APP_NAME))
    } else {
        Ok(PathBuf::from(home).join(format!(".{APP_NAME}")))
    }
}

fn data_dir() -> VaultResult<PathBuf> {
    Ok(appdata_root()?.join("Data"))
}

fn data_path(name: &str) -> VaultResult<PathBuf> {
    Ok(data_dir()?.join(name))
}

fn ensure_data_dir() -> VaultResult<()> {
    fs::create_dir_all(data_dir()?).map_err(|error| VaultError::Io(error.to_string()))
}

fn load_or_create_salt() -> VaultResult<Vec<u8>> {
    ensure_data_dir()?;
    let path = data_path("salt.bin")?;
    if !path.exists() {
        let mut salt = [0u8; 16];
        OsRng.fill_bytes(&mut salt);
        fs::write(&path, salt).map_err(|error| VaultError::Io(error.to_string()))?;
    }
    fs::read(path).map_err(|error| VaultError::Io(error.to_string()))
}

fn derive_key(master_password: &str) -> VaultResult<[u8; 32]> {
    if master_password.trim().is_empty() {
        return Err(VaultError::MissingMasterPassword);
    }

    let salt = load_or_create_salt()?;
    let mut key = [0u8; 32];
    pbkdf2_hmac::<Sha256>(master_password.as_bytes(), &salt, ITERATIONS, &mut key);
    Ok(key)
}

fn encrypt_message(message: &str, master_password: &str) -> VaultResult<String> {
    let key = derive_key(master_password)?;
    let cipher = Aes256Gcm::new_from_slice(&key)
        .map_err(|_| VaultError::Data("Could not create encryption key.".into()))?;
    let mut nonce_bytes = [0u8; NONCE_LEN];
    OsRng.fill_bytes(&mut nonce_bytes);
    let ciphertext = cipher
        .encrypt(Nonce::from_slice(&nonce_bytes), message.as_bytes())
        .map_err(|_| VaultError::Data("Encryption failed.".into()))?;

    let mut token = Vec::with_capacity(NONCE_LEN + ciphertext.len());
    token.extend_from_slice(&nonce_bytes);
    token.extend_from_slice(&ciphertext);

    Ok(format!("{TOKEN_PREFIX}{}", URL_SAFE_NO_PAD.encode(token)))
}

fn decrypt_message(token: &str, master_password: &str) -> VaultResult<String> {
    let encoded = token
        .strip_prefix(TOKEN_PREFIX)
        .ok_or(VaultError::DecryptionFailed)?;
    let token_bytes = URL_SAFE_NO_PAD
        .decode(encoded.as_bytes())
        .map_err(|_| VaultError::DecryptionFailed)?;

    if token_bytes.len() <= NONCE_LEN {
        return Err(VaultError::DecryptionFailed);
    }

    let key = derive_key(master_password)?;
    let cipher = Aes256Gcm::new_from_slice(&key)
        .map_err(|_| VaultError::Data("Could not create encryption key.".into()))?;
    let (nonce_bytes, ciphertext) = token_bytes.split_at(NONCE_LEN);
    let plaintext = cipher
        .decrypt(Nonce::from_slice(nonce_bytes), ciphertext)
        .map_err(|_| VaultError::DecryptionFailed)?;
    String::from_utf8(plaintext).map_err(|error| VaultError::Data(error.to_string()))
}

fn read_json_file(path: &Path) -> VaultResult<Value> {
    ensure_data_dir()?;
    if !path.exists() {
        fs::write(path, "{}").map_err(|error| VaultError::Io(error.to_string()))?;
        return Ok(json!({}));
    }

    let content = fs::read_to_string(path).map_err(|error| VaultError::Io(error.to_string()))?;
    match serde_json::from_str(&content) {
        Ok(value) => Ok(value),
        Err(_) => {
            let backup = path.with_file_name("password_backup.json");
            let _ = fs::rename(path, backup);
            fs::write(path, "{}").map_err(|error| VaultError::Io(error.to_string()))?;
            Ok(json!({}))
        }
    }
}

fn password_data() -> VaultResult<Map<String, Value>> {
    let value = read_json_file(&data_path("password.json")?)?;
    Ok(value.as_object().cloned().unwrap_or_default())
}

fn write_password_data(data: &Map<String, Value>) -> VaultResult<()> {
    ensure_data_dir()?;
    let content = serde_json::to_string_pretty(data).map_err(|error| VaultError::Data(error.to_string()))?;
    fs::write(data_path("password.json")?, content).map_err(|error| VaultError::Io(error.to_string()))
}

fn entry_user_token(entry: &Value) -> Option<&str> {
    entry
        .get("username")
        .or_else(|| entry.get("user"))
        .and_then(Value::as_str)
}

fn normalize_entries(value: &Value) -> Vec<Value> {
    if let Some(entries) = value.as_array() {
        entries.clone()
    } else if value.is_object() {
        vec![value.clone()]
    } else {
        Vec::new()
    }
}

fn decrypted_entries(site: &str, master_password: &str) -> VaultResult<Vec<Credential>> {
    let data = password_data()?;
    let site_value = data.get(site).ok_or(VaultError::SiteNotFound)?;
    let entries = normalize_entries(site_value);
    let mut result = Vec::with_capacity(entries.len());

    for entry in entries {
        let user_token = entry_user_token(&entry).ok_or_else(|| VaultError::Data("Missing username token.".into()))?;
        let password_token = entry
            .get("password")
            .and_then(Value::as_str)
            .ok_or_else(|| VaultError::Data("Missing password token.".into()))?;

        result.push(Credential {
            user: decrypt_message(user_token, master_password)?,
            password: decrypt_message(password_token, master_password)?,
        });
    }

    Ok(result)
}

#[tauri::command]
fn store_password(
    site: String,
    username: String,
    password: String,
    master_password: String,
    replace_existing: bool,
) -> Result<(), String> {
    let clean_site = site.trim();
    let clean_username = username.trim();
    let clean_password = password.trim();

    if clean_site.is_empty() || clean_username.is_empty() || clean_password.is_empty() {
        return Err(VaultError::Data("Site, username, and password are required.".into()).into());
    }

    let mut data = password_data()?;

    if let Some(existing) = data.get(clean_site).cloned() {
        let mut entries = normalize_entries(&existing);
        let mut duplicate_index = None;

        for (index, entry) in entries.iter().enumerate() {
            if let Some(token) = entry_user_token(entry) {
                if decrypt_message(token, &master_password).ok().as_deref() == Some(clean_username) {
                    duplicate_index = Some(index);
                    break;
                }
            }
        }

        if duplicate_index.is_some() && !replace_existing {
            return Err(VaultError::DuplicateEntry.into());
        }

        if let Some(index) = duplicate_index {
            entries.remove(index);
        }

        entries.push(json!({
            "username": encrypt_message(clean_username, &master_password)?,
            "password": encrypt_message(clean_password, &master_password)?,
        }));
        data.insert(clean_site.to_string(), Value::Array(entries));
    } else {
        data.insert(
            clean_site.to_string(),
            Value::Array(vec![json!({
                "username": encrypt_message(clean_username, &master_password)?,
                "password": encrypt_message(clean_password, &master_password)?,
            })]),
        );
    }

    write_password_data(&data)?;
    Ok(())
}

#[tauri::command]
fn get_site_data(site: String, master_password: String) -> Result<Vec<Credential>, String> {
    Ok(decrypted_entries(&site, &master_password)?)
}

#[tauri::command]
fn get_site_display_names(master_password: String) -> Result<Vec<SiteDisplayItem>, String> {
    let data = password_data()?;
    let mut items = Vec::new();

    for (site, value) in data.iter() {
        let entries = normalize_entries(value);
        if entries.len() <= 1 {
            items.push(SiteDisplayItem {
                label: site.clone(),
                site: site.clone(),
                username: None,
            });
            continue;
        }

        for entry in entries {
            let username = entry_user_token(&entry)
                .and_then(|token| decrypt_message(token, &master_password).ok())
                .unwrap_or_else(|| "<error>".into());
            items.push(SiteDisplayItem {
                label: format!("{site} | {username}"),
                site: site.clone(),
                username: Some(username),
            });
        }
    }

    items.sort_by(|left, right| left.label.to_lowercase().cmp(&right.label.to_lowercase()));
    Ok(items)
}

#[tauri::command]
fn delete_password(site: String, username: Option<String>, master_password: String) -> Result<(), String> {
    let mut data = password_data()?;
    let Some(existing) = data.get(&site).cloned() else {
        return Err(VaultError::SiteNotFound.into());
    };

    if username.is_none() {
        data.remove(&site);
        write_password_data(&data)?;
        return Ok(());
    }

    let target = username.unwrap_or_default();
    let entries = normalize_entries(&existing);
    let mut retained = Vec::new();
    let mut deleted = false;

    for entry in entries {
        let matches = entry_user_token(&entry)
            .and_then(|token| decrypt_message(token, &master_password).ok())
            .map(|decrypted| decrypted == target)
            .unwrap_or(false);

        if matches {
            deleted = true;
        } else {
            retained.push(entry);
        }
    }

    if !deleted {
        return Err(VaultError::EntryNotFound.into());
    }

    if retained.is_empty() {
        data.remove(&site);
    } else {
        data.insert(site, Value::Array(retained));
    }

    write_password_data(&data)?;
    Ok(())
}

#[tauri::command]
fn get_theme() -> Result<String, String> {
    let path = data_path("themes.json")?;
    let value = read_json_file(&path)?;
    let accent = value
        .get("theme")
        .and_then(|theme| {
            theme
                .get("accent")
                .and_then(Value::as_str)
                .or_else(|| theme.as_str())
        })
        .unwrap_or("#8B5CF6");

    Ok(accent.to_string())
}

#[tauri::command]
fn set_theme(accent_color: String) -> Result<(), String> {
    ensure_data_dir()?;
    let value = json!({
        "theme": {
            "accent": accent_color
        }
    });
    let content = serde_json::to_string_pretty(&value).map_err(|error| VaultError::Data(error.to_string()))?;
    fs::write(data_path("themes.json")?, content).map_err(|error| VaultError::Io(error.to_string()).into())
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_clipboard_manager::init())
        .invoke_handler(tauri::generate_handler![
            store_password,
            get_site_data,
            get_site_display_names,
            delete_password,
            get_theme,
            set_theme
        ])
        .run(tauri::generate_context!())
        .expect("error while running VaultMLN");
}
