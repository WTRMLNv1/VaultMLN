import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { invoke } from "@tauri-apps/api/core";
import { writeText } from "@tauri-apps/plugin-clipboard-manager";
import {
  AlertTriangle,
  Check,
  Clipboard,
  Eye,
  EyeOff,
  KeyRound,
  LayoutDashboard,
  Lock,
  LogOut,
  Palette,
  Plus,
  Search,
  Settings,
  ShieldCheck,
  Trash2,
  UserCircle,
  Users,
} from "lucide-react";
import "./styles.css";

const DEFAULT_ACCENT = "#8B5CF6";
const SCREENS = {
  ACCOUNTS: "accounts",
  CREATE_ACCOUNT: "create-account",
  UNLOCK: "unlock",
  HOME: "home",
  ADD: "add",
  VIEW: "view",
  DELETE: "delete",
  SETTINGS: "settings",
};

const SCREEN_META = {
  [SCREENS.ACCOUNTS]: ["Accounts", "Choose a vault profile"],
  [SCREENS.CREATE_ACCOUNT]: ["Create account", "Set up a new encrypted vault"],
  [SCREENS.UNLOCK]: ["Unlock Vault", "Enter your master password"],
  [SCREENS.HOME]: ["Home", "Welcome back"],
  [SCREENS.ADD]: ["Add Password", "Save a new encrypted login"],
  [SCREENS.VIEW]: ["View Passwords", "Search and reveal saved logins"],
  [SCREENS.DELETE]: ["Delete Password", "Remove a saved credential"],
  [SCREENS.SETTINGS]: ["Settings", "Customize your experience"],
};

function App() {
  const [screen, setScreen] = useState(SCREENS.ACCOUNTS);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [session, setSession] = useState(null);
  const [accent, setAccent] = useState(DEFAULT_ACCENT);
  const [siteItems, setSiteItems] = useState([]);
  const [stats, setStats] = useState({ entry_count: 0, account_count: 0, last_added: null });
  const [message, setMessage] = useState(null);

  const showMessage = (text, tone = "info") => {
    setMessage({ text, tone });
    window.setTimeout(() => setMessage(null), 3200);
  };

  const loadAccounts = async () => {
    const rows = await invoke("list_accounts");
    setAccounts(rows);
    if (rows.length === 0) {
      setScreen(SCREENS.CREATE_ACCOUNT);
    }
    return rows;
  };

  const refreshVault = async (nextSession = session) => {
    if (!nextSession) {
      setSiteItems([]);
      setStats({ entry_count: 0, account_count: accounts.length, last_added: null });
      return;
    }
    const [items, nextStats] = await Promise.all([
      invoke("get_site_display_names", {
        accountId: nextSession.accountId,
        masterPassword: nextSession.masterPassword,
      }),
      invoke("get_vault_stats", { accountId: nextSession.accountId }),
    ]);
    setSiteItems(items);
    setStats(nextStats);
  };

  useEffect(() => {
    loadAccounts().catch((error) => showMessage(String(error), "error"));
    invoke("get_theme")
      .then((value) => setAccent(value || DEFAULT_ACCENT))
      .catch(() => setAccent(DEFAULT_ACCENT));
  }, []);

  useEffect(() => {
    document.documentElement.style.setProperty("--accent", accent);
  }, [accent]);

  const navigate = async (next) => {
    if (session && [SCREENS.HOME, SCREENS.VIEW, SCREENS.DELETE].includes(next)) {
      await refreshVault();
    }
    setScreen(next);
  };

  const lockSession = async () => {
    setSession(null);
    setSelectedAccount(null);
    setSiteItems([]);
    await loadAccounts();
    setScreen(SCREENS.ACCOUNTS);
  };

  const meta = SCREEN_META[screen] || SCREEN_META[SCREENS.HOME];
  const locked = !session;

  return (
    <main className="app-root">
      <div className="shell">
        {!locked && (
          <Sidebar
            screen={screen}
            navigate={navigate}
            session={session}
            lockSession={lockSession}
          />
        )}
        <section className="main">
          {!locked && (
            <header className="topbar">
              <div>
                <div className="topbar-title">{meta[0]}</div>
                <div className="topbar-sub">{meta[1]}</div>
              </div>
              <button className="icon-btn" title="Lock vault" onClick={lockSession}>
                <Lock size={16} />
              </button>
            </header>
          )}

          <div className={locked ? "content locked-content" : "content"}>
            <StatusToast message={message} />
            {screen === SCREENS.ACCOUNTS && (
              <AccountSelect
                accounts={accounts}
                onCreate={() => setScreen(SCREENS.CREATE_ACCOUNT)}
                onSelect={(account) => {
                  setSelectedAccount(account);
                  setScreen(SCREENS.UNLOCK);
                }}
                onDelete={async (account) => {
                  if (!window.confirm(`Delete account "${account.display_name}" and all of its passwords?`)) return;
                  await invoke("delete_account", { accountId: account.id });
                  showMessage("Account deleted.", "success");
                  await loadAccounts();
                }}
              />
            )}
            {screen === SCREENS.CREATE_ACCOUNT && (
              <CreateAccount
                onBack={() => setScreen(accounts.length ? SCREENS.ACCOUNTS : SCREENS.CREATE_ACCOUNT)}
                onCreated={async (account, masterPassword) => {
                  const nextSession = {
                    accountId: account.id,
                    displayName: account.display_name,
                    masterPassword,
                  };
                  setSession(nextSession);
                  setSelectedAccount(null);
                  await loadAccounts();
                  await refreshVault(nextSession);
                  setScreen(SCREENS.HOME);
                  showMessage("Account created.", "success");
                }}
                showMessage={showMessage}
              />
            )}
            {screen === SCREENS.UNLOCK && selectedAccount && (
              <UnlockScreen
                account={selectedAccount}
                onBack={() => setScreen(SCREENS.ACCOUNTS)}
                onUnlocked={async (account, masterPassword) => {
                  const nextSession = {
                    accountId: account.id,
                    displayName: account.display_name,
                    masterPassword,
                  };
                  setSession(nextSession);
                  await refreshVault(nextSession);
                  setScreen(SCREENS.HOME);
                  showMessage("Vault unlocked.", "success");
                }}
                showMessage={showMessage}
              />
            )}
            {screen === SCREENS.HOME && session && (
              <HomeScreen stats={stats} navigate={navigate} />
            )}
            {screen === SCREENS.ADD && session && (
              <AddScreen
                session={session}
                onSaved={async () => {
                  showMessage("Password saved.", "success");
                  await refreshVault();
                  setScreen(SCREENS.HOME);
                }}
                showMessage={showMessage}
              />
            )}
            {screen === SCREENS.VIEW && session && (
              <ViewScreen session={session} items={siteItems} showMessage={showMessage} />
            )}
            {screen === SCREENS.DELETE && session && (
              <DeleteScreen
                session={session}
                items={siteItems}
                refreshVault={refreshVault}
                showMessage={showMessage}
              />
            )}
            {screen === SCREENS.SETTINGS && session && (
              <SettingsScreen
                session={session}
                accent={accent}
                setAccent={setAccent}
                showMessage={showMessage}
                lockSession={lockSession}
                refreshVault={refreshVault}
              />
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

function StatusToast({ message }) {
  if (!message) return null;
  return <div className={`toast ${message.tone}`}>{message.text}</div>;
}

function Sidebar({ screen, navigate, session, lockSession }) {
  const nav = [
    [SCREENS.HOME, LayoutDashboard, "Home"],
    [SCREENS.ADD, Plus, "Add Password"],
    [SCREENS.VIEW, Eye, "View Passwords"],
    [SCREENS.DELETE, Trash2, "Delete"],
    [SCREENS.SETTINGS, Settings, "Settings"],
  ];
  const initials = getInitials(session.displayName);

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon"><Lock size={17} /></div>
        <span>VaultMLN</span>
      </div>
      <div className="nav-section">Vault</div>
      {nav.slice(0, 4).map(([id, Icon, label]) => (
        <button key={id} className={`nav-item ${screen === id ? "active" : ""}`} onClick={() => navigate(id)}>
          <Icon size={17} />
          {label}
        </button>
      ))}
      <div className="nav-section system-section">System</div>
      {nav.slice(4).map(([id, Icon, label]) => (
        <button key={id} className={`nav-item ${screen === id ? "active" : ""}`} onClick={() => navigate(id)}>
          <Icon size={17} />
          {label}
        </button>
      ))}
      <div className="sidebar-bottom">
        <div className="account-status">
          <div className="avatar">{initials}</div>
          <div>
            <strong>{session.displayName}</strong>
            <span>Session active</span>
          </div>
          <button className="small-icon-btn" title="Switch account" onClick={lockSession}>
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </aside>
  );
}

function AccountSelect({ accounts, onCreate, onSelect, onDelete }) {
  return (
    <div className="auth-wrap wide-auth">
      <div className="lock-icon-wrap"><Users size={31} /></div>
      <h1>Choose account</h1>
      <p>Each account has its own master password, salt, and encrypted vault.</p>
      <div className="account-grid">
        {accounts.map((account) => (
          <button key={account.id} className="account-card" onClick={() => onSelect(account)}>
            <div className="avatar">{getInitials(account.display_name)}</div>
            <div>
              <strong>{account.display_name}</strong>
              <span>Open vault</span>
            </div>
            <span
              className="delete-account"
              onClick={(event) => {
                event.stopPropagation();
                onDelete(account);
              }}
              title="Delete account"
            >
              <Trash2 size={15} />
            </span>
          </button>
        ))}
      </div>
      <button className="btn-primary" onClick={onCreate}>
        <Plus size={16} />
        New account
      </button>
    </div>
  );
}

function CreateAccount({ onBack, onCreated, showMessage }) {
  const [form, setForm] = useState({ displayName: "", password: "", confirm: "" });
  const [visible, setVisible] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    const displayName = form.displayName.trim();
    const password = form.password.trim();
    if (!displayName || !password) {
      showMessage("Display name and password are required.", "error");
      return;
    }
    if (password !== form.confirm.trim()) {
      showMessage("Passwords do not match.", "error");
      return;
    }
    try {
      const account = await invoke("create_account", { displayName, masterPassword: password });
      await onCreated(account, password);
    } catch (error) {
      showMessage(String(error), "error");
    }
  };

  return (
    <div className="auth-wrap">
      <div className="lock-icon-wrap"><UserCircle size={31} /></div>
      <h1>Create account</h1>
      <p>Start with a display name and master password for this vault.</p>
      <form className="form-grid" onSubmit={submit}>
        <Field label="Display name">
          <input autoFocus value={form.displayName} onChange={(event) => setForm({ ...form, displayName: event.target.value })} placeholder="Ansh" />
        </Field>
        <Field label="Master password">
          <div className="field-wrap">
            <input type={visible ? "text" : "password"} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} placeholder="Master password" />
            <button type="button" className="eye-btn" onClick={() => setVisible((value) => !value)}>{visible ? <EyeOff size={17} /> : <Eye size={17} />}</button>
          </div>
        </Field>
        <Field label="Confirm password">
          <input type={visible ? "text" : "password"} value={form.confirm} onChange={(event) => setForm({ ...form, confirm: event.target.value })} placeholder="Confirm password" />
        </Field>
        <button className="btn-primary"><ShieldCheck size={16} />Create and unlock</button>
      </form>
      <button className="ghost-link" type="button" onClick={onBack}>Back to accounts</button>
    </div>
  );
}

function UnlockScreen({ account, onBack, onUnlocked, showMessage }) {
  const [password, setPassword] = useState("");
  const [visible, setVisible] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    if (!password.trim()) return;
    try {
      const unlocked = await invoke("unlock_account", {
        accountId: account.id,
        masterPassword: password,
      });
      await onUnlocked(unlocked, password);
    } catch (error) {
      showMessage(String(error), "error");
    }
  };

  return (
    <div className="auth-wrap">
      <div className="lock-icon-wrap"><Lock size={31} /></div>
      <h1>Unlocking: {account.display_name}</h1>
      <p>Enter this account&apos;s master password to open the session.</p>
      <form className="form-grid" onSubmit={submit}>
        <Field label="Master password">
          <div className="field-wrap">
            <input autoFocus type={visible ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter master password" />
            <button type="button" className="eye-btn" onClick={() => setVisible((value) => !value)}>{visible ? <EyeOff size={17} /> : <Eye size={17} />}</button>
          </div>
        </Field>
        <button className="btn-primary" disabled={!password.trim()}><ShieldCheck size={16} />Unlock</button>
      </form>
      <button className="ghost-link" type="button" onClick={onBack}>Back to accounts</button>
    </div>
  );
}

function HomeScreen({ stats, navigate }) {
  return (
    <>
      <div className="stat-row">
        <StatCard accent label="Stored entries" value={stats.entry_count} sub="logins tracked" />
        <StatCard label="Last added" value={stats.last_added || "None"} sub={stats.last_added ? "most recent site" : "add your first entry"} mono />
        <StatCard label="Encryption" value="AES-256" sub="PBKDF2 - 390k reps" />
      </div>
      <div className="quick-actions">
        <div className="section-label">Quick actions</div>
        <div className="action-cards">
          <ActionCard icon={Plus} title="Add Password" subtitle="Save a new encrypted login" onClick={() => navigate(SCREENS.ADD)} />
          <ActionCard icon={Eye} title="View Passwords" subtitle="Search and reveal saved logins" onClick={() => navigate(SCREENS.VIEW)} />
          <ActionCard icon={Trash2} danger title="Delete Entry" subtitle="Remove a saved credential" onClick={() => navigate(SCREENS.DELETE)} />
        </div>
      </div>
    </>
  );
}

function StatCard({ label, value, sub, accent, mono }) {
  return (
    <div className={`stat-card ${accent ? "accent-card" : ""}`}>
      <div className="label">{label}</div>
      <div className={`value ${mono ? "mono-value" : ""}`}>{value}</div>
      <div className="sub">{sub}</div>
    </div>
  );
}

function ActionCard({ icon: Icon, title, subtitle, danger, onClick }) {
  return (
    <button className={`action-card ${danger ? "danger" : ""}`} onClick={onClick}>
      <Icon size={20} />
      <span>{title}</span>
      <small>{subtitle}</small>
    </button>
  );
}

function AddScreen({ session, onSaved, showMessage }) {
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
        accountId: session.accountId,
        site,
        username,
        password,
        masterPassword: session.masterPassword,
        replaceExisting: false,
      });
      await onSaved();
    } catch (error) {
      if (String(error).includes("DUPLICATE_ENTRY")) {
        const replace = window.confirm(`Replace the saved password for ${site} / ${username}?`);
        if (!replace) return;
        await invoke("store_password", {
          accountId: session.accountId,
          site,
          username,
          password,
          masterPassword: session.masterPassword,
          replaceExisting: true,
        });
        await onSaved();
        return;
      }
      showMessage(String(error), "error");
    }
  };

  return (
    <div className="form-card">
      <form className="form-grid" onSubmit={submit}>
        <Field label="Site"><input value={form.site} onChange={update("site")} placeholder="github.com" /></Field>
        <Field label="Username or email"><input value={form.username} onChange={update("username")} placeholder="name@example.com" /></Field>
        <Field label="Password">
          <div className="field-wrap">
            <input type={visible ? "text" : "password"} value={form.password} onChange={update("password")} placeholder="Password" />
            <button type="button" className="eye-btn" onClick={() => setVisible((value) => !value)}>{visible ? <EyeOff size={17} /> : <Eye size={17} />}</button>
          </div>
        </Field>
        <Field label="Confirm password"><input type={visible ? "text" : "password"} value={form.confirm} onChange={update("confirm")} placeholder="Confirm password" /></Field>
        <button className="btn-save"><Check size={15} />Save Entry</button>
      </form>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="field-group">
      <span className="field-label">{label}</span>
      {children}
    </label>
  );
}

function SitePicker({ items, selected, setSelected }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    const clean = query.trim().toLowerCase();
    if (!clean) return items;
    return items.filter((item) => `${item.site} ${item.username} ${item.label}`.toLowerCase().includes(clean));
  }, [items, query]);

  return (
    <div className="list-panel">
      <div className="list-search">
        <Search size={16} />
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search sites..." />
      </div>
      <div className="list-items">
        {filtered.length === 0 && <div className="empty-state">No sites found</div>}
        {filtered.map((item) => (
          <button
            key={item.id}
            className={`list-item ${selected?.id === item.id ? "selected" : ""}`}
            onClick={() => setSelected(item)}
          >
            <span className="site">{item.site}</span>
            <span className="user">{item.username}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function ViewScreen({ session, items, showMessage }) {
  const [selected, setSelected] = useState(null);
  const [entry, setEntry] = useState(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setEntry(null);
    setVisible(false);
  }, [selected?.id]);

  const loadEntry = async () => {
    if (!selected) {
      showMessage("Choose a site first.", "error");
      return;
    }
    try {
      const nextEntry = await invoke("get_password", {
        accountId: session.accountId,
        entryId: selected.id,
        masterPassword: session.masterPassword,
      });
      setEntry(nextEntry);
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
    <div className="site-list-wrap">
      <SitePicker items={items} selected={selected} setSelected={setSelected} />
      <div className="detail-panel">
        {!entry ? (
          <div className="detail-empty">
            <KeyRound size={32} />
            Select an entry, then get data
            <button className="btn-get" onClick={loadEntry}><Eye size={14} />Get Data</button>
          </div>
        ) : (
          <>
            <DetailRow label="Username / email" value={entry.user} />
            <div className="detail-row">
              <div className="dlabel">Password</div>
              <div className="detail-val">
                <span>{visible ? entry.password : "•".repeat(Math.min(entry.password.length, 18))}</span>
                <div className="detail-actions">
                  <button className="icon-btn" title="Copy" onClick={copyPassword}><Clipboard size={16} /></button>
                  <button className="icon-btn" title="Reveal" onClick={() => setVisible((value) => !value)}>
                    {visible ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function DetailRow({ label, value }) {
  return (
    <div className="detail-row">
      <div className="dlabel">{label}</div>
      <div className="detail-val"><span>{value}</span></div>
    </div>
  );
}

function DeleteScreen({ session, items, refreshVault, showMessage }) {
  const [selected, setSelected] = useState(null);

  const deleteSelected = async () => {
    if (!selected) {
      showMessage("Choose a site first.", "error");
      return;
    }
    if (!window.confirm(`Delete ${selected.site} - ${selected.username}?`)) return;
    try {
      await invoke("delete_password", {
        accountId: session.accountId,
        entryId: selected.id,
        masterPassword: session.masterPassword,
      });
      setSelected(null);
      await refreshVault();
      showMessage("Entry deleted.", "success");
    } catch (error) {
      showMessage(String(error), "error");
    }
  };

  return (
    <div className="site-list-wrap">
      <SitePicker items={items} selected={selected} setSelected={setSelected} />
      <div className="detail-panel">
        {!selected ? (
          <div className="detail-empty"><Trash2 size={32} />Select an entry to delete</div>
        ) : (
          <>
            <DetailRow label="Selected entry" value={`${selected.site} - ${selected.username}`} />
            <p className="danger-copy">This action is permanent and cannot be undone.</p>
            <button className="btn-danger" onClick={deleteSelected}><Trash2 size={14} />Delete Entry</button>
          </>
        )}
      </div>
    </div>
  );
}

function SettingsScreen({ session, accent, setAccent, showMessage, lockSession, refreshVault }) {
  const [changeForm, setChangeForm] = useState({ oldPassword: "", newPassword: "", confirm: "" });
  const colors = ["#8B5CF6", "#2563EB", "#059669", "#DC2626", "#D97706", "#0F766E", "#DB2777"];

  const saveAccent = async (value) => {
    setAccent(value);
    await invoke("set_theme", { accentColor: value });
    showMessage("Theme updated.", "success");
  };

  const changePassword = async () => {
    if (!changeForm.oldPassword || !changeForm.newPassword) {
      showMessage("Fill in both password fields.", "error");
      return;
    }
    if (changeForm.newPassword !== changeForm.confirm) {
      showMessage("New passwords do not match.", "error");
      return;
    }
    await invoke("change_master_password", {
      accountId: session.accountId,
      oldPassword: changeForm.oldPassword,
      newPassword: changeForm.newPassword,
    });
    showMessage("Master password changed. Unlock again.", "success");
    await lockSession();
  };

  const wipePasswords = async () => {
    if (!window.confirm("Wipe all passwords in this account?")) return;
    await invoke("wipe_account_passwords", {
      accountId: session.accountId,
      masterPassword: session.masterPassword,
    });
    await refreshVault();
    showMessage("Passwords wiped.", "success");
  };

  return (
    <div className="settings-wrap">
      <section className="settings-section">
        <div className="settings-label">Accent color</div>
        <div className="swatch-row">
          {colors.map((value) => (
            <button
              key={value}
              className={`swatch ${accent === value ? "active" : ""}`}
              style={{ "--swatch": value }}
              onClick={() => saveAccent(value)}
              aria-label={`Use ${value}`}
            />
          ))}
        </div>
      </section>
      <section className="settings-section">
        <div className="settings-label">Danger zone</div>
        <div className="danger-card">
          <h3><AlertTriangle size={15} />Destructive actions</h3>
          <p>Changing your master password re-encrypts all entries in this account. Wiping passwords is irreversible.</p>
          <div className="change-password-grid">
            <input type="password" placeholder="Current password" value={changeForm.oldPassword} onChange={(event) => setChangeForm({ ...changeForm, oldPassword: event.target.value })} />
            <input type="password" placeholder="New password" value={changeForm.newPassword} onChange={(event) => setChangeForm({ ...changeForm, newPassword: event.target.value })} />
            <input type="password" placeholder="Confirm new password" value={changeForm.confirm} onChange={(event) => setChangeForm({ ...changeForm, confirm: event.target.value })} />
          </div>
          <div className="danger-btns">
            <button className="btn-change-pw" onClick={changePassword}>Change Password</button>
            <button className="btn-wipe" onClick={wipePasswords}>Wipe All Passwords</button>
          </div>
        </div>
      </section>
    </div>
  );
}

function getInitials(name = "") {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "??";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
}

createRoot(document.getElementById("root")).render(<App />);
