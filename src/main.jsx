import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { invoke } from "@tauri-apps/api/core";
import { writeText } from "@tauri-apps/plugin-clipboard-manager";
import {
  ArrowLeft,
  Check,
  Clipboard,
  Eye,
  EyeOff,
  KeyRound,
  Lock,
  Palette,
  Plus,
  Search,
  Shield,
  Trash2,
} from "lucide-react";
import "./styles.css";
import logo from "../assets/VaultMLN.png";

const DEFAULT_ACCENT = "#8B5CF6";
const SCREENS = {
  UNLOCK: "unlock",
  HOME: "home",
  ADD: "add",
  VIEW: "view",
  DELETE: "delete",
  SETTINGS: "settings",
};

function App() {
  const [screen, setScreen] = useState(SCREENS.UNLOCK);
  const [masterPassword, setMasterPassword] = useState("");
  const [accent, setAccent] = useState(DEFAULT_ACCENT);
  const [siteItems, setSiteItems] = useState([]);
  const [message, setMessage] = useState(null);

  const showMessage = (text, tone = "info") => {
    setMessage({ text, tone });
    window.setTimeout(() => setMessage(null), 3600);
  };

  const refreshSites = async () => {
    if (!masterPassword) {
      setSiteItems([]);
      return;
    }
    try {
      const items = await invoke("get_site_display_names", { masterPassword });
      setSiteItems(items);
    } catch {
      setSiteItems([]);
    }
  };

  useEffect(() => {
    invoke("get_theme")
      .then((value) => setAccent(value || DEFAULT_ACCENT))
      .catch(() => setAccent(DEFAULT_ACCENT));
  }, []);

  useEffect(() => {
    document.documentElement.style.setProperty("--accent", accent);
  }, [accent]);

  useEffect(() => {
    refreshSites();
  }, [masterPassword]);

  const navigate = async (next) => {
    if (next === SCREENS.HOME || next === SCREENS.VIEW || next === SCREENS.DELETE) {
      await refreshSites();
    }
    setScreen(next);
  };

  return (
    <main className="app-shell">
      <div className="app-panel">
        <StatusToast message={message} />
        {screen !== SCREENS.UNLOCK && (
          <button className="icon-button back-button" onClick={() => navigate(SCREENS.HOME)} aria-label="Back home">
            <ArrowLeft size={20} />
          </button>
        )}

        {screen === SCREENS.UNLOCK && (
          <UnlockScreen
            masterPassword={masterPassword}
            setMasterPassword={setMasterPassword}
            onUnlock={() => navigate(SCREENS.HOME)}
          />
        )}
        {screen === SCREENS.HOME && (
          <HomeScreen siteCount={siteItems.length} navigate={navigate} />
        )}
        {screen === SCREENS.ADD && (
          <AddScreen
            masterPassword={masterPassword}
            onSaved={async () => {
              showMessage("Password saved.", "success");
              await navigate(SCREENS.HOME);
            }}
            showMessage={showMessage}
          />
        )}
        {screen === SCREENS.VIEW && (
          <ViewScreen masterPassword={masterPassword} items={siteItems} refreshSites={refreshSites} showMessage={showMessage} />
        )}
        {screen === SCREENS.DELETE && (
          <DeleteScreen
            masterPassword={masterPassword}
            items={siteItems}
            refreshSites={refreshSites}
            showMessage={showMessage}
          />
        )}
        {screen === SCREENS.SETTINGS && (
          <SettingsScreen accent={accent} setAccent={setAccent} showMessage={showMessage} />
        )}
      </div>
    </main>
  );
}

function StatusToast({ message }) {
  if (!message) return null;
  return <div className={`toast ${message.tone}`}>{message.text}</div>;
}

function ScreenTitle({ icon: Icon, title, subtitle }) {
  return (
    <header className="screen-header">
      <div className="title-icon">
        <Icon size={22} />
      </div>
      <div>
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
    </header>
  );
}

function UnlockScreen({ masterPassword, setMasterPassword, onUnlock }) {
  const [visible, setVisible] = useState(false);
  const canUnlock = masterPassword.trim().length > 0;

  return (
    <section className="unlock-layout">
      <img src={logo} alt="VaultMLN" className="brand-mark" />
      <ScreenTitle icon={Lock} title="Unlock VaultMLN" subtitle="Enter your master password to open this session." />
      <form
        className="form-stack"
        onSubmit={(event) => {
          event.preventDefault();
          if (canUnlock) onUnlock();
        }}
      >
        <label>
          Master password
          <div className="field-with-button">
            <input
              autoFocus
              type={visible ? "text" : "password"}
              value={masterPassword}
              onChange={(event) => setMasterPassword(event.target.value)}
              placeholder="Master password"
            />
            <button type="button" className="icon-button" onClick={() => setVisible((value) => !value)} aria-label="Toggle password">
              {visible ? <EyeOff size={19} /> : <Eye size={19} />}
            </button>
          </div>
        </label>
        <button className="primary-action" disabled={!canUnlock}>
          <Shield size={18} />
          Unlock
        </button>
      </form>
    </section>
  );
}

function HomeScreen({ siteCount, navigate }) {
  return (
    <section className="home-layout">
      <div className="home-top">
        <img src={logo} alt="VaultMLN" className="home-logo" />
        <div className="count-panel">
          <span>Stored entries</span>
          <strong>{siteCount}</strong>
        </div>
      </div>
      <div className="action-grid">
        <button onClick={() => navigate(SCREENS.ADD)}>
          <Plus size={20} />
          Add Password
        </button>
        <button onClick={() => navigate(SCREENS.VIEW)}>
          <Search size={20} />
          View Passwords
        </button>
        <button onClick={() => navigate(SCREENS.DELETE)}>
          <Trash2 size={20} />
          Delete Password
        </button>
        <button onClick={() => navigate(SCREENS.SETTINGS)}>
          <Palette size={20} />
          Settings
        </button>
      </div>
    </section>
  );
}

function AddScreen({ masterPassword, onSaved, showMessage }) {
  const [form, setForm] = useState({ site: "", username: "", password: "", confirm: "" });
  const [visible, setVisible] = useState(false);

  const update = (field) => (event) => setForm((current) => ({ ...current, [field]: event.target.value }));

  const submit = async (event) => {
    event.preventDefault();
    const site = form.site.trim();
    const username = form.username.trim();
    const password = form.password.trim();
    if (!site || !username || !password) {
      showMessage("Fill in every field first.", "error");
      return;
    }
    if (password !== form.confirm.trim()) {
      showMessage("Passwords do not match.", "error");
      return;
    }
    try {
      await invoke("store_password", {
        site,
        username,
        password,
        masterPassword,
        replaceExisting: false,
      });
      await onSaved();
    } catch (error) {
      if (String(error).includes("DUPLICATE_ENTRY")) {
        const replace = window.confirm(`Replace the saved password for ${site} / ${username}?`);
        if (!replace) return;
        await invoke("store_password", {
          site,
          username,
          password,
          masterPassword,
          replaceExisting: true,
        });
        await onSaved();
        return;
      }
      showMessage(String(error), "error");
    }
  };

  return (
    <section>
      <ScreenTitle icon={Plus} title="Add Password" subtitle="Save a new encrypted login." />
      <form className="form-stack" onSubmit={submit}>
        <label>
          Site
          <input value={form.site} onChange={update("site")} placeholder="example.com" />
        </label>
        <label>
          Username or email
          <input value={form.username} onChange={update("username")} placeholder="name@example.com" />
        </label>
        <label>
          Password
          <div className="field-with-button">
            <input type={visible ? "text" : "password"} value={form.password} onChange={update("password")} placeholder="Password" />
            <button type="button" className="icon-button" onClick={() => setVisible((value) => !value)} aria-label="Toggle password">
              {visible ? <EyeOff size={19} /> : <Eye size={19} />}
            </button>
          </div>
        </label>
        <label>
          Confirm password
          <input type={visible ? "text" : "password"} value={form.confirm} onChange={update("confirm")} placeholder="Confirm password" />
        </label>
        <button className="primary-action">
          <Check size={18} />
          Save
        </button>
      </form>
    </section>
  );
}

function SitePicker({ items, selected, setSelected }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    const clean = query.trim().toLowerCase();
    if (!clean) return items;
    return items.filter((item) => item.label.toLowerCase().includes(clean));
  }, [items, query]);

  return (
    <div className="site-picker">
      <div className="search-input">
        <Search size={18} />
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search sites" />
      </div>
      <div className="site-list">
        {filtered.length === 0 && <div className="empty-state">No sites found</div>}
        {filtered.map((item) => (
          <button
            key={`${item.site}:${item.username ?? ""}:${item.label}`}
            className={selected?.label === item.label ? "selected" : ""}
            onClick={() => setSelected(item)}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function ViewScreen({ masterPassword, items, showMessage }) {
  const [selected, setSelected] = useState(null);
  const [entry, setEntry] = useState(null);
  const [visible, setVisible] = useState(false);

  const loadEntry = async () => {
    if (!selected) {
      showMessage("Choose a site first.", "error");
      return;
    }
    try {
      const entries = await invoke("get_site_data", { site: selected.site, masterPassword });
      const exact = selected.username ? entries.find((item) => item.user === selected.username) : entries[0];
      setEntry(exact || entries[0] || null);
      setVisible(false);
    } catch (error) {
      showMessage(String(error), "error");
    }
  };

  const copyPassword = async () => {
    if (!entry?.password) return;
    await writeText(entry.password);
    showMessage("Password copied.", "success");
  };

  return (
    <section>
      <ScreenTitle icon={Search} title="View Passwords" subtitle="Search and reveal saved logins." />
      <SitePicker items={items} selected={selected} setSelected={setSelected} />
      <button className="primary-action compact" onClick={loadEntry}>Get Data</button>
      <div className="result-panel">
        <div>
          <span>Username / email</span>
          <strong>{entry?.user || "No entry selected"}</strong>
        </div>
        <div>
          <span>Password</span>
          <strong>{entry ? (visible ? entry.password : "*".repeat(entry.password.length)) : "No entry selected"}</strong>
        </div>
        <div className="inline-actions">
          <button className="icon-button" onClick={copyPassword} disabled={!entry} aria-label="Copy password">
            <Clipboard size={18} />
          </button>
          <button className="icon-button" onClick={() => setVisible((value) => !value)} disabled={!entry} aria-label="Toggle password">
            {visible ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
      </div>
    </section>
  );
}

function DeleteScreen({ masterPassword, items, refreshSites, showMessage }) {
  const [selected, setSelected] = useState(null);

  const deleteSelected = async () => {
    if (!selected) {
      showMessage("Choose a site first.", "error");
      return;
    }
    const confirmed = window.confirm(`Delete ${selected.label}?`);
    if (!confirmed) return;
    try {
      await invoke("delete_password", {
        site: selected.site,
        username: selected.username,
        masterPassword,
      });
      setSelected(null);
      await refreshSites();
      showMessage("Entry deleted.", "success");
    } catch (error) {
      showMessage(String(error), "error");
    }
  };

  return (
    <section>
      <ScreenTitle icon={Trash2} title="Delete Password" subtitle="Remove one saved login or a single-site entry." />
      <SitePicker items={items} selected={selected} setSelected={setSelected} />
      <button className="danger-action" onClick={deleteSelected}>
        <Trash2 size={18} />
        Delete Selected
      </button>
    </section>
  );
}

function SettingsScreen({ accent, setAccent, showMessage }) {
  const colors = ["#8B5CF6", "#2563EB", "#059669", "#DC2626", "#D97706", "#0F766E"];

  const saveAccent = async (value) => {
    setAccent(value);
    await invoke("set_theme", { accentColor: value });
    showMessage("Theme updated.", "success");
  };

  return (
    <section>
      <ScreenTitle icon={Palette} title="Settings" subtitle="Choose the app accent color." />
      <div className="swatch-grid">
        {colors.map((value) => (
          <button
            key={value}
            className={accent === value ? "active" : ""}
            style={{ "--swatch": value }}
            onClick={() => saveAccent(value)}
            aria-label={`Use ${value}`}
          />
        ))}
      </div>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);
