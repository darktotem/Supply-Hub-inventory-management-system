import { useState } from "react";
import Login, { roleNames } from "../features/auth/login";
import Employees from "../features/admin/employees";
import Dashboard from "../features/admin/dashboard";
import { changePassword, clearSession } from "../api/auth";

/**
 * @typedef {{
 *   id: number,
 *   name: string,
 *   username: string,
 *   email?: string | null,
 *   role: string,
 *   is_active: boolean,
 *   must_change_password: boolean,
 *   created_at?: string | null
 * }} AuthUser
 */

export default function AppRoutes() {
  const [user, setUser] = /** @type {[AuthUser | null, import("react").Dispatch<import("react").SetStateAction<AuthUser | null>>]} */ (
    useState(/** @type {AuthUser | null} */ (null))
  );
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (!user) return <Login onAuthenticated={setUser} />;

  if (user.must_change_password) {
    return (
      <RequiredPasswordChange
        user={user}
        onChanged={(updatedUser) => setUser(updatedUser)}
      />
    );
  }

  const navigation = user.role === "it_admin"
    ? [{ href: "#employees", label: "Employees" }]
    : [{ href: "#dashboard", label: "Dashboard" }];

  function signOut() {
    clearSession();
    setMobileMenuOpen(false);
    setUser(null);
  }

  return (
    <div className="app-shell">
      <header className="navbar">
        <div className="brand">
          <span className="brand-mark">SH</span>
          <strong>Supply Hub</strong>
        </div>

        <nav className="navbar-links" aria-label="Main navigation">
          {navigation.map((item) => (
            <a key={item.href} href={item.href} className="active">
              {item.label}
            </a>
          ))}
        </nav>

        <div className="navbar-user">
          <div>
            <strong>{user.name}</strong>
            <span>{/** @type {Record<string, string>} */ (roleNames)[user.role] || user.role}</span>
          </div>
          <button className="logout-button" type="button" onClick={signOut}>Sign out</button>
        </div>

        <button
          className="hamburger-button"
          type="button"
          aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
          aria-expanded={mobileMenuOpen}
          onClick={() => setMobileMenuOpen((open) => !open)}
        >
          <span></span><span></span><span></span>
        </button>
      </header>

      <aside className={`sidebar ${mobileMenuOpen ? "sidebar-open" : ""}`} aria-hidden={!mobileMenuOpen}>
        <nav aria-label="Mobile navigation">
          {navigation.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="active"
              onClick={() => setMobileMenuOpen(false)}
            >
              {item.label}
            </a>
          ))}
        </nav>
        <button className="logout-button" type="button" onClick={signOut}>Sign out</button>
      </aside>

      {mobileMenuOpen && (
        <button
          className="sidebar-overlay"
          type="button"
          aria-label="Close navigation menu"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <main className="main-content">
        {user.role === "it_admin" ? <Employees /> : <Dashboard />}
      </main>
    </div>
  );
}

/** @param {{ user: AuthUser, onChanged: (user: AuthUser) => void }} props */
function RequiredPasswordChange({ user, onChanged }) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      await changePassword(oldPassword, newPassword);
      onChanged({ ...user, must_change_password: false });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to change password");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">Security</p>
        <h1>Change your password</h1>
        <p className="form-help">
          Your administrator requires a new password before you continue.
        </p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={submit}>
          <label htmlFor="old-password">Current password</label>
          <input
            id="old-password"
            type="password"
            value={oldPassword}
            onChange={(event) => setOldPassword(event.target.value)}
            required
          />

          <label htmlFor="required-new-password">New password</label>
          <input
            id="required-new-password"
            type="password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            minLength={8}
            required
          />

          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "Updating…" : "Continue"}
          </button>
        </form>
      </section>
    </main>
  );
}
