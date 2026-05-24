use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use hmac::{Hmac, Mac};
use pbkdf2::pbkdf2_hmac;
use rand::{rngs::OsRng, RngCore};
use serde::{Deserialize, Serialize};
use serde_json::json;
use sha2::Sha256;
use std::{
    env, fs,
    path::{Path, PathBuf},
    time::{SystemTime, UNIX_EPOCH},
};
use thiserror::Error;

const APP_NAME: &str = "VaultMLN";
const ITERATIONS: u32 = 390_000;
const NONCE_LEN: usize = 12;
const VERIFIER_CONTEXT: &[u8] = b"vaultmln-account-verifier-v1";

type VaultResult<T> = Result<T, VaultError>;
type HmacSha256 = Hmac<Sha256>;

#[derive(Debug, Error)]
enum VaultError {
    #[error("Master password is required.")]
    MissingMasterPassword,
    #[error("Account not found.")]
    AccountNotFound,
    #[error("Invalid master password.")]
    InvalidMasterPassword,
    #[error("Password entry not found.")]
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

impl From<VaultError> for String {
    fn from(value: VaultError) -> Self {
        value.to_string()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct AccountRecord {
    id: i64,
    display_name: String,
    password_hash: String,
    salt: String,
    created_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct PasswordRecord {
    id: i64,
    account_id: i64,
    site: String,
    username_enc: String,
    username_nonce: String,
    password_enc: String,
    password_nonce: String,
    created_at: i64,
    updated_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct VaultDb {
    next_account_id: i64,
    next_password_id: i64,
    accounts: Vec<AccountRecord>,
    passwords: Vec<PasswordRecord>,
}

#[derive(Debug, Clone, Serialize)]
struct AccountMeta {
    id: i64,
    display_name: String,
    created_at: i64,
}

#[derive(Debug, Clone, Serialize)]
struct Credential {
    id: i64,
    site: String,
    user: String,
    password: String,
}

#[derive(Debug, Clone, Serialize)]
struct SiteDisplayItem {
    id: i64,
    label: String,
    site: String,
    username: String,
}

#[derive(Debug, Clone, Serialize)]
struct VaultStats {
    entry_count: usize,
    account_count: usize,
    last_added: Option<String>,
}

impl Default for VaultDb {
    fn default() -> Self {
        Self {
            next_account_id: 1,
            next_password_id: 1,
            accounts: Vec::new(),
            passwords: Vec::new(),
        }
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

fn now() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_secs() as i64)
        .unwrap_or_default()
}

fn db_path() -> VaultResult<PathBuf> {
    data_path("vault.db.json")
}

fn read_json_file(path: &Path) -> VaultResult<serde_json::Value> {
    ensure_data_dir()?;
    if !path.exists() {
        fs::write(path, "{}").map_err(|error| VaultError::Io(error.to_string()))?;
        return Ok(json!({}));
    }

    let content = fs::read_to_string(path).map_err(|error| VaultError::Io(error.to_string()))?;
    match serde_json::from_str(&content) {
        Ok(value) => Ok(value),
        Err(_) => {
            let backup = path.with_extension("backup.json");
            let _ = fs::rename(path, backup);
            fs::write(path, "{}").map_err(|error| VaultError::Io(error.to_string()))?;
            Ok(json!({}))
        }
    }
}

fn read_db() -> VaultResult<VaultDb> {
    ensure_data_dir()?;
    let path = db_path()?;
    if !path.exists() {
        let db = VaultDb::default();
        write_db(&db)?;
        return Ok(db);
    }

    let content = fs::read_to_string(&path).map_err(|error| VaultError::Io(error.to_string()))?;
    serde_json::from_str(&content).map_err(|error| VaultError::Data(error.to_string()))
}

fn write_db(db: &VaultDb) -> VaultResult<()> {
    ensure_data_dir()?;
    let content = serde_json::to_string_pretty(db).map_err(|error| VaultError::Data(error.to_string()))?;
    fs::write(db_path()?, content).map_err(|error| VaultError::Io(error.to_string()))
}

fn random_bytes<const N: usize>() -> [u8; N] {
    let mut bytes = [0u8; N];
    OsRng.fill_bytes(&mut bytes);
    bytes
}

fn derive_key(master_password: &str, salt: &[u8]) -> VaultResult<[u8; 32]> {
    if master_password.trim().is_empty() {
        return Err(VaultError::MissingMasterPassword);
    }

    let mut key = [0u8; 32];
    pbkdf2_hmac::<Sha256>(master_password.as_bytes(), salt, ITERATIONS, &mut key);
    Ok(key)
}

fn hash_key(key: &[u8; 32]) -> VaultResult<String> {
    let mut mac = <HmacSha256 as Mac>::new_from_slice(key)
        .map_err(|error| VaultError::Data(error.to_string()))?;
    mac.update(VERIFIER_CONTEXT);
    Ok(URL_SAFE_NO_PAD.encode(mac.finalize().into_bytes()))
}

fn constant_time_eq(left: &str, right: &str) -> bool {
    let left = left.as_bytes();
    let right = right.as_bytes();
    if left.len() != right.len() {
        return false;
    }

    left.iter()
        .zip(right.iter())
        .fold(0u8, |acc, (a, b)| acc | (a ^ b))
        == 0
}

fn account_key(account_id: i64, master_password: &str) -> VaultResult<[u8; 32]> {
    let db = read_db()?;
    let account = db
        .accounts
        .iter()
        .find(|account| account.id == account_id)
        .ok_or(VaultError::AccountNotFound)?;
    let salt = URL_SAFE_NO_PAD
        .decode(account.salt.as_bytes())
        .map_err(|_| VaultError::Data("Account salt is invalid.".into()))?;
    let key = derive_key(master_password, &salt)?;
    let hash = hash_key(&key)?;
    if !constant_time_eq(&hash, &account.password_hash) {
        return Err(VaultError::InvalidMasterPassword);
    }
    Ok(key)
}

fn encrypt_field(message: &str, key: &[u8; 32]) -> VaultResult<(String, String)> {
    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|_| VaultError::Data("Could not create encryption key.".into()))?;
    let nonce_bytes = random_bytes::<NONCE_LEN>();
    let ciphertext = cipher
        .encrypt(Nonce::from_slice(&nonce_bytes), message.as_bytes())
        .map_err(|_| VaultError::Data("Encryption failed.".into()))?;
    Ok((URL_SAFE_NO_PAD.encode(ciphertext), URL_SAFE_NO_PAD.encode(nonce_bytes)))
}

fn decrypt_field(ciphertext: &str, nonce: &str, key: &[u8; 32]) -> VaultResult<String> {
    let cipher = Aes256Gcm::new_from_slice(key)
        .map_err(|_| VaultError::Data("Could not create encryption key.".into()))?;
    let nonce_bytes = URL_SAFE_NO_PAD
        .decode(nonce.as_bytes())
        .map_err(|_| VaultError::DecryptionFailed)?;
    let ciphertext = URL_SAFE_NO_PAD
        .decode(ciphertext.as_bytes())
        .map_err(|_| VaultError::DecryptionFailed)?;
    let plaintext = cipher
        .decrypt(Nonce::from_slice(&nonce_bytes), ciphertext.as_ref())
        .map_err(|_| VaultError::DecryptionFailed)?;
    String::from_utf8(plaintext).map_err(|error| VaultError::Data(error.to_string()))
}

fn decrypt_record(record: &PasswordRecord, key: &[u8; 32]) -> VaultResult<Credential> {
    Ok(Credential {
        id: record.id,
        site: record.site.clone(),
        user: decrypt_field(&record.username_enc, &record.username_nonce, key)?,
        password: decrypt_field(&record.password_enc, &record.password_nonce, key)?,
    })
}

#[tauri::command]
fn list_accounts() -> Result<Vec<AccountMeta>, String> {
    let db = read_db()?;
    Ok(db
        .accounts
        .into_iter()
        .map(|account| AccountMeta {
            id: account.id,
            display_name: account.display_name,
            created_at: account.created_at,
        })
        .collect())
}

#[tauri::command]
fn create_account(display_name: String, master_password: String) -> Result<AccountMeta, String> {
    let clean_name = display_name.trim();
    if clean_name.is_empty() {
        return Err(VaultError::Data("Display name is required.".into()).into());
    }

    let salt = random_bytes::<32>();
    let key = derive_key(&master_password, &salt)?;
    let password_hash = hash_key(&key)?;
    let mut db = read_db()?;
    let account = AccountRecord {
        id: db.next_account_id,
        display_name: clean_name.to_string(),
        password_hash,
        salt: URL_SAFE_NO_PAD.encode(salt),
        created_at: now(),
    };
    db.next_account_id += 1;
    db.accounts.push(account.clone());
    write_db(&db)?;
    Ok(AccountMeta {
        id: account.id,
        display_name: account.display_name,
        created_at: account.created_at,
    })
}

#[tauri::command]
fn unlock_account(account_id: i64, master_password: String) -> Result<AccountMeta, String> {
    let _key = account_key(account_id, &master_password)?;
    let db = read_db()?;
    let account = db
        .accounts
        .into_iter()
        .find(|account| account.id == account_id)
        .ok_or(VaultError::AccountNotFound)?;
    Ok(AccountMeta {
        id: account.id,
        display_name: account.display_name,
        created_at: account.created_at,
    })
}

#[tauri::command]
fn delete_account(account_id: i64) -> Result<(), String> {
    let mut db = read_db()?;
    let original_len = db.accounts.len();
    db.accounts.retain(|account| account.id != account_id);
    if db.accounts.len() == original_len {
        return Err(VaultError::AccountNotFound.into());
    }
    db.passwords.retain(|entry| entry.account_id != account_id);
    write_db(&db)?;
    Ok(())
}

#[tauri::command]
fn store_password(
    account_id: i64,
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

    let key = account_key(account_id, &master_password)?;
    let mut db = read_db()?;
    let duplicate_index = db.passwords.iter().position(|entry| {
        entry.account_id == account_id
            && entry.site == clean_site
            && decrypt_field(&entry.username_enc, &entry.username_nonce, &key)
                .ok()
                .as_deref()
                == Some(clean_username)
    });

    if duplicate_index.is_some() && !replace_existing {
        return Err(VaultError::DuplicateEntry.into());
    }

    let (username_enc, username_nonce) = encrypt_field(clean_username, &key)?;
    let (password_enc, password_nonce) = encrypt_field(clean_password, &key)?;
    let timestamp = now();

    if let Some(index) = duplicate_index {
        db.passwords[index].username_enc = username_enc;
        db.passwords[index].username_nonce = username_nonce;
        db.passwords[index].password_enc = password_enc;
        db.passwords[index].password_nonce = password_nonce;
        db.passwords[index].updated_at = timestamp;
    } else {
        db.passwords.push(PasswordRecord {
            id: db.next_password_id,
            account_id,
            site: clean_site.to_string(),
            username_enc,
            username_nonce,
            password_enc,
            password_nonce,
            created_at: timestamp,
            updated_at: timestamp,
        });
        db.next_password_id += 1;
    }

    write_db(&db)?;
    Ok(())
}

#[tauri::command]
fn get_password(account_id: i64, entry_id: i64, master_password: String) -> Result<Credential, String> {
    let key = account_key(account_id, &master_password)?;
    let db = read_db()?;
    let entry = db
        .passwords
        .iter()
        .find(|entry| entry.account_id == account_id && entry.id == entry_id)
        .ok_or(VaultError::EntryNotFound)?;
    Ok(decrypt_record(entry, &key)?)
}

#[tauri::command]
fn get_site_display_names(account_id: i64, master_password: String) -> Result<Vec<SiteDisplayItem>, String> {
    let key = account_key(account_id, &master_password)?;
    let db = read_db()?;
    let mut items = Vec::new();
    let account_entries: Vec<&PasswordRecord> = db
        .passwords
        .iter()
        .filter(|entry| entry.account_id == account_id)
        .collect();

    for entry in account_entries.iter() {
        let username = decrypt_field(&entry.username_enc, &entry.username_nonce, &key)?;
        let same_site_count = account_entries
            .iter()
            .filter(|candidate| candidate.site == entry.site)
            .count();
        let label = if same_site_count > 1 {
            format!("{} | {}", entry.site, username)
        } else {
            entry.site.clone()
        };

        items.push(SiteDisplayItem {
            id: entry.id,
            label,
            site: entry.site.clone(),
            username,
        });
    }

    items.sort_by(|left, right| left.label.to_lowercase().cmp(&right.label.to_lowercase()));
    Ok(items)
}

#[tauri::command]
fn delete_password(account_id: i64, entry_id: i64, master_password: String) -> Result<(), String> {
    let _key = account_key(account_id, &master_password)?;
    let mut db = read_db()?;
    let original_len = db.passwords.len();
    db.passwords
        .retain(|entry| !(entry.account_id == account_id && entry.id == entry_id));
    if db.passwords.len() == original_len {
        return Err(VaultError::EntryNotFound.into());
    }
    write_db(&db)?;
    Ok(())
}

#[tauri::command]
fn wipe_account_passwords(account_id: i64, master_password: String) -> Result<(), String> {
    let _key = account_key(account_id, &master_password)?;
    let mut db = read_db()?;
    db.passwords.retain(|entry| entry.account_id != account_id);
    write_db(&db)?;
    Ok(())
}

#[tauri::command]
fn change_master_password(account_id: i64, old_password: String, new_password: String) -> Result<(), String> {
    let old_key = account_key(account_id, &old_password)?;
    let new_salt = random_bytes::<32>();
    let new_key = derive_key(&new_password, &new_salt)?;
    let new_hash = hash_key(&new_key)?;
    let mut db = read_db()?;

    for entry in db.passwords.iter_mut().filter(|entry| entry.account_id == account_id) {
        let username = decrypt_field(&entry.username_enc, &entry.username_nonce, &old_key)?;
        let password = decrypt_field(&entry.password_enc, &entry.password_nonce, &old_key)?;
        let (username_enc, username_nonce) = encrypt_field(&username, &new_key)?;
        let (password_enc, password_nonce) = encrypt_field(&password, &new_key)?;
        entry.username_enc = username_enc;
        entry.username_nonce = username_nonce;
        entry.password_enc = password_enc;
        entry.password_nonce = password_nonce;
        entry.updated_at = now();
    }

    let account = db
        .accounts
        .iter_mut()
        .find(|account| account.id == account_id)
        .ok_or(VaultError::AccountNotFound)?;
    account.salt = URL_SAFE_NO_PAD.encode(new_salt);
    account.password_hash = new_hash;

    write_db(&db)?;
    Ok(())
}

#[tauri::command]
fn get_vault_stats(account_id: i64) -> Result<VaultStats, String> {
    let db = read_db()?;
    let mut entries: Vec<&PasswordRecord> = db
        .passwords
        .iter()
        .filter(|entry| entry.account_id == account_id)
        .collect();
    entries.sort_by(|left, right| right.created_at.cmp(&left.created_at));
    Ok(VaultStats {
        entry_count: entries.len(),
        account_count: db.accounts.len(),
        last_added: entries.first().map(|entry| entry.site.clone()),
    })
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
                .and_then(serde_json::Value::as_str)
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
            list_accounts,
            create_account,
            unlock_account,
            delete_account,
            store_password,
            get_password,
            get_site_display_names,
            delete_password,
            wipe_account_passwords,
            change_master_password,
            get_vault_stats,
            get_theme,
            set_theme
        ])
        .run(tauri::generate_context!())
        .expect("error while running VaultMLN");
}
