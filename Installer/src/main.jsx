import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { getCurrentWindow } from "@tauri-apps/api/window";
import "./styles.css";

const SCREENS = {
  WELCOME: "welcome",
  INSTALLING: "installing",
  DONE: "done",
  ERROR: "error",
};

const FALLBACK_CONFIG = {
  version: "2.0.0",
  app_name: "VaultMLN",
  publisher: "Melogne Studio",
  description: "Encrypted password manager",
};

function App() {
  const [screen, setScreen] = useState(SCREENS.WELCOME);
  const [config, setConfig] = useState(FALLBACK_CONFIG);
  const [installPath, setInstallPath] = useState("");
  const [desktopShortcut, setDesktopShortcut] = useState(true);
  const [startMenuShortcut, setStartMenuShortcut] = useState(true);
  const [alreadyInstalled, setAlreadyInstalled] = useState(false);
  const [progress, setProgress] = useState({ step: "Preparing...", percent: 0 });
  const [errorMsg, setErrorMsg] = useState("");
  const [editingPath, setEditingPath] = useState(false);

  useEffect(() => {
    invoke("get_config").then(setConfig).catch(() => setConfig(FALLBACK_CONFIG));
    invoke("get_default_install_path").then(setInstallPath);
    invoke("check_existing_install").then(setAlreadyInstalled);
  }, []);

  const closeWindow = () => getCurrentWindow().close();

  const startInstall = async () => {
    setScreen(SCREENS.INSTALLING);
    setProgress({ step: "Preparing...", percent: 0 });
    const unlisten = await listen("install_progress", (event) => {
      setProgress(event.payload);
    });

    try {
      await invoke("run_install", {
        installPath,
        createDesktopShortcut: desktopShortcut,
        createStartMenuShortcut: startMenuShortcut,
      });
      setScreen(SCREENS.DONE);
    } catch (error) {
      setErrorMsg(String(error));
      setScreen(SCREENS.ERROR);
    } finally {
      unlisten();
    }
  };

  const launchAndClose = async () => {
    try {
      await invoke("launch_app", { installPath });
    } catch {
      // The install succeeded, so close even if launch is blocked.
    }
    await closeWindow();
  };

  return (
    <div className="app" data-tauri-drag-region>
      <TitleBar version={config.version} onClose={closeWindow} />
      <main className="content">
        {screen === SCREENS.WELCOME && (
          <WelcomeScreen
            config={config}
            installPath={installPath}
            setInstallPath={setInstallPath}
            desktopShortcut={desktopShortcut}
            setDesktopShortcut={setDesktopShortcut}
            startMenuShortcut={startMenuShortcut}
            setStartMenuShortcut={setStartMenuShortcut}
            alreadyInstalled={alreadyInstalled}
            editingPath={editingPath}
            setEditingPath={setEditingPath}
            onInstall={startInstall}
            onClose={closeWindow}
          />
        )}
        {screen === SCREENS.INSTALLING && <InstallingScreen progress={progress} />}
        {screen === SCREENS.DONE && (
          <DoneScreen config={config} installPath={installPath} onLaunch={launchAndClose} onClose={closeWindow} />
        )}
        {screen === SCREENS.ERROR && <ErrorScreen message={errorMsg} onClose={closeWindow} />}
      </main>
    </div>
  );
}

function TitleBar({ version, onClose }) {
  return (
    <header className="titlebar" data-tauri-drag-region>
      <div className="titlebar-left" data-tauri-drag-region>
        <div className="titlebar-icon"><LockIcon size={17} /></div>
        <span className="titlebar-name">VaultMLN Setup</span>
        <span className="titlebar-version">v{version}</span>
      </div>
      <button className="titlebar-close" onClick={onClose} aria-label="Close">
        <CloseIcon />
      </button>
    </header>
  );
}

function WelcomeScreen({
  config,
  installPath,
  setInstallPath,
  desktopShortcut,
  setDesktopShortcut,
  startMenuShortcut,
  setStartMenuShortcut,
  alreadyInstalled,
  editingPath,
  setEditingPath,
  onInstall,
  onClose,
}) {
  return (
    <section className="screen welcome-screen">
      <div className="welcome-left">
        <div className="app-icon-wrap"><LockIcon size={36} /></div>
        <div>
          <h1 className="app-name">{config.app_name}</h1>
          <p className="app-desc">{config.description}</p>
        </div>
        <div className="app-meta">
          <MetaRow label="Version" value={`v${config.version}`} />
          <MetaRow label="Publisher" value={config.publisher} />
          <MetaRow label="Platform" value="Windows x64" />
        </div>
        {alreadyInstalled && (
          <div className="already-badge">
            <CheckIcon size={13} />
            Already installed, will update
          </div>
        )}
      </div>

      <div className="welcome-right">
        <div className="options-section">
          <div className="option-label">Install location</div>
          {editingPath ? (
            <input
              className="path-input"
              value={installPath}
              onChange={(event) => setInstallPath(event.target.value)}
              onBlur={() => setEditingPath(false)}
              onKeyDown={(event) => {
                if (event.key === "Enter") setEditingPath(false);
              }}
              autoFocus
              spellCheck={false}
            />
          ) : (
            <button className="path-display" onClick={() => setEditingPath(true)}>
              <span className="path-text">{installPath}</span>
              <span className="path-edit">edit</span>
            </button>
          )}
        </div>

        <div className="options-section">
          <div className="option-label">Shortcuts</div>
          <Toggle checked={desktopShortcut} onChange={setDesktopShortcut} label="Desktop shortcut" />
          <Toggle checked={startMenuShortcut} onChange={setStartMenuShortcut} label="Start Menu entry" />
        </div>

        <div className="action-row">
          <button className="btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn-install" onClick={onInstall}>
            {alreadyInstalled ? "Update" : "Install"}
            <ArrowIcon />
          </button>
        </div>
      </div>
    </section>
  );
}

function InstallingScreen({ progress }) {
  return (
    <section className="screen center-screen">
      <div className="spinner-wrap">
        <div className="spinner-ring" />
        <div className="spinner-icon"><LockIcon size={20} /></div>
      </div>
      <h2 className="status-title">Installing VaultMLN</h2>
      <p className="status-sub">{progress.step}</p>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${progress.percent}%` }} />
      </div>
      <span className="progress-pct">{progress.percent}%</span>
    </section>
  );
}

function DoneScreen({ config, installPath, onLaunch, onClose }) {
  return (
    <section className="screen center-screen">
      <div className="done-icon"><CheckIcon size={28} /></div>
      <h2 className="status-title">Installation complete</h2>
      <p className="status-sub">VaultMLN v{config.version} was installed to</p>
      <code className="done-path">{installPath}\\VaultMLN.exe</code>
      <div className="action-row centered">
        <button className="btn-ghost" onClick={onClose}>Close</button>
        <button className="btn-install" onClick={onLaunch}>
          Launch VaultMLN
          <ArrowIcon />
        </button>
      </div>
    </section>
  );
}

function ErrorScreen({ message, onClose }) {
  return (
    <section className="screen center-screen">
      <div className="error-icon"><AlertIcon /></div>
      <h2 className="status-title">Installation failed</h2>
      <p className="error-msg">{message}</p>
      <div className="action-row centered">
        <button className="btn-install" onClick={onClose}>Close</button>
      </div>
    </section>
  );
}

function MetaRow({ label, value }) {
  return (
    <div className="meta-row">
      <span className="meta-label">{label}</span>
      <span className="meta-value">{value}</span>
    </div>
  );
}

function Toggle({ checked, onChange, label }) {
  return (
    <label className="toggle-row">
      <button type="button" className={`toggle-track ${checked ? "on" : ""}`} onClick={() => onChange(!checked)}>
        <span className="toggle-thumb" />
      </button>
      <span className="toggle-label">{label}</span>
    </label>
  );
}

function LockIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );
}

function CheckIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 6L9 17l-5-5" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12h14M12 5l7 7-7 7" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <path d="M1 1L9 9M9 1L1 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

function AlertIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round">
      <circle cx="12" cy="12" r="10" />
      <path d="M12 8v4M12 16h.01" />
    </svg>
  );
}

createRoot(document.getElementById("root")).render(<App />);
