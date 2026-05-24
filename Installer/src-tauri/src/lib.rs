use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use tauri::{Emitter, Manager};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct InstallerConfig {
    pub version: String,
    pub app_name: String,
    pub publisher: String,
    pub description: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct InstallProgress {
    pub step: String,
    pub percent: u32,
}

#[derive(Debug, thiserror::Error)]
pub enum InstallError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("{0}")]
    Other(String),
}

impl Serialize for InstallError {
    fn serialize<S>(&self, serializer: S) -> std::result::Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        serializer.serialize_str(&self.to_string())
    }
}

type Result<T> = std::result::Result<T, InstallError>;

mod commands {
    use super::*;

    #[tauri::command]
    pub fn get_config(app: tauri::AppHandle) -> Result<InstallerConfig> {
        let resource_path = assets_dir(&app)?.join("installer_config.json");
        let raw = fs::read_to_string(&resource_path)?;
        Ok(serde_json::from_str(&raw)?)
    }

    #[tauri::command]
    pub fn get_default_install_path() -> String {
        let program_files = std::env::var("ProgramFiles").unwrap_or_else(|_| "C:\\Program Files".to_string());
        format!("{}\\VaultMLN", program_files)
    }

    #[tauri::command]
    pub fn check_existing_install() -> bool {
        Path::new(&get_default_install_path()).join("VaultMLN.exe").exists()
    }

    #[tauri::command]
    pub async fn run_install(
        app: tauri::AppHandle,
        install_path: String,
        create_desktop_shortcut: bool,
        create_start_menu_shortcut: bool,
    ) -> Result<()> {
        let config = get_config(app.clone())?;
        emit_progress(&app, "Creating install directory...", 10);
        let install_dir = PathBuf::from(&install_path);
        fs::create_dir_all(&install_dir)?;

        emit_progress(&app, "Copying application files...", 30);
        let src_exe = assets_dir(&app)?.join("app").join("VaultMLN.exe");
        let dst_exe = install_dir.join("VaultMLN.exe");

        if !src_exe.exists() {
            return Err(InstallError::Other(
                "VaultMLN.exe not found. Place it at Installer/assets/app/VaultMLN.exe".to_string(),
            ));
        }

        fs::copy(&src_exe, &dst_exe)?;

        emit_progress(&app, "Writing version info...", 50);
        fs::write(
            install_dir.join("installer_config.json"),
            serde_json::to_string_pretty(&config)?,
        )?;

        if create_desktop_shortcut {
            emit_progress(&app, "Creating desktop shortcut...", 65);
            create_shortcut_windows(
                &dst_exe,
                &desktop_path().join("VaultMLN.lnk"),
                "VaultMLN - Password Manager",
            )?;
        }

        if create_start_menu_shortcut {
            emit_progress(&app, "Creating Start Menu entry...", 75);
            let start_menu_dir = start_menu_path().join("VaultMLN");
            fs::create_dir_all(&start_menu_dir)?;
            create_shortcut_windows(
                &dst_exe,
                &start_menu_dir.join("VaultMLN.lnk"),
                "VaultMLN - Password Manager",
            )?;
        }

        emit_progress(&app, "Registering uninstaller...", 88);
        write_uninstall_registry(&config, &install_dir, &dst_exe)?;

        emit_progress(&app, "Done.", 100);
        Ok(())
    }

    #[tauri::command]
    pub fn launch_app(install_path: String) -> Result<()> {
        let exe = PathBuf::from(&install_path).join("VaultMLN.exe");
        std::process::Command::new(&exe)
            .spawn()
            .map_err(|error| InstallError::Other(format!("Failed to launch: {error}")))?;
        Ok(())
    }
}

fn emit_progress(app: &tauri::AppHandle, step: &str, percent: u32) {
    let _ = app.emit(
        "install_progress",
        InstallProgress {
            step: step.to_string(),
            percent,
        },
    );
}

fn assets_dir(app: &tauri::AppHandle) -> Result<PathBuf> {
    Ok(app
        .path()
        .resource_dir()
        .map_err(|error| InstallError::Other(error.to_string()))?
        .join("assets"))
}

fn desktop_path() -> PathBuf {
    std::env::var("USERPROFILE")
        .map(PathBuf::from)
        .unwrap_or_default()
        .join("Desktop")
}

fn start_menu_path() -> PathBuf {
    PathBuf::from(std::env::var("APPDATA").unwrap_or_default())
        .join("Microsoft")
        .join("Windows")
        .join("Start Menu")
        .join("Programs")
}

fn ps_escape(value: &Path) -> String {
    value.display().to_string().replace('\'', "''")
}

fn create_shortcut_windows(target: &Path, link: &Path, description: &str) -> Result<()> {
    let script = format!(
        "$ws = New-Object -ComObject WScript.Shell; \
         $s = $ws.CreateShortcut('{}'); \
         $s.TargetPath = '{}'; \
         $s.Description = '{}'; \
         $s.Save()",
        ps_escape(link),
        ps_escape(target),
        description.replace('\'', "''"),
    );
    let output = std::process::Command::new("powershell")
        .args(["-NoProfile", "-NonInteractive", "-Command", &script])
        .output()
        .map_err(|error| InstallError::Other(format!("PowerShell error: {error}")))?;

    if !output.status.success() {
        return Err(InstallError::Other("Failed to create shortcut.".to_string()));
    }

    Ok(())
}

fn write_uninstall_registry(config: &InstallerConfig, install_dir: &Path, exe: &Path) -> Result<()> {
    let uninstall_cmd = format!(
        "powershell -NoProfile -ExecutionPolicy Bypass -Command \"Remove-Item -LiteralPath '{}' -Recurse -Force\"",
        ps_escape(install_dir)
    );
    let script = format!(
        "$r = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\VaultMLN'; \
         New-Item -Path $r -Force | Out-Null; \
         Set-ItemProperty -Path $r -Name 'DisplayName' -Value '{}'; \
         Set-ItemProperty -Path $r -Name 'DisplayVersion' -Value '{}'; \
         Set-ItemProperty -Path $r -Name 'Publisher' -Value '{}'; \
         Set-ItemProperty -Path $r -Name 'InstallLocation' -Value '{}'; \
         Set-ItemProperty -Path $r -Name 'UninstallString' -Value '{}'; \
         Set-ItemProperty -Path $r -Name 'DisplayIcon' -Value '{}';",
        config.app_name.replace('\'', "''"),
        config.version.replace('\'', "''"),
        config.publisher.replace('\'', "''"),
        ps_escape(install_dir),
        uninstall_cmd.replace('\'', "''"),
        ps_escape(exe),
    );
    let output = std::process::Command::new("powershell")
        .args(["-NoProfile", "-NonInteractive", "-Command", &script])
        .output()
        .map_err(|error| InstallError::Other(format!("Registry error: {error}")))?;

    if !output.status.success() {
        return Err(InstallError::Other("Failed to write uninstall registry entry.".to_string()));
    }

    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            commands::get_config,
            commands::get_default_install_path,
            commands::check_existing_install,
            commands::run_install,
            commands::launch_app,
        ])
        .run(tauri::generate_context!())
        .expect("error running installer");
}
