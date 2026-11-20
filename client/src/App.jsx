import { useEffect, useState } from "react";
import Login, { roleNames } from "./features/auth/login";
import Employees from "./features/admin/employees";
import Dashboard from "./features/admin/dashboard";
import Customers from "./features/sales/customers";
import CustomerOrders from "./features/sales/customer_orders";
import { changePassword, clearSession, getSavedUser, getSavedToken } from "./api/auth";

// The role name the backend uses for the sales officer (check it matches the backend)
const SALES_ROLE = "sales_officer";

// Reads the page name from the address bar: "#customers" gives "customers"
function getPageFromHash() {
  return window.location.hash.replace("#", "");
}

export default function App() {
  const [user, setUser] = useState(() => {
    const savedUser = getSavedUser();
    return getSavedToken() && savedUser ? savedUser : null;
  });
  const [page, setPage] = useState(getPageFromHash());

  // Update the page when the link in the address bar changes
  useEffect(() => {
    function handleHashChange() {
      setPage(getPageFromHash());
    }
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  if (!user) return <Login onAuthenticated={setUser} />;

  if (user.must_change_password) {
    return <RequiredPasswordChange user={user} onChanged={(updatedUser) => setUser(updatedUser)} />;
  }

  const isSales = user.role === SALES_ROLE;
  const activePage = isSales && (page === "customers" || page === "orders") ? page : "dashboard";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">SH</span><strong>Supply Hub</strong></div>
        <nav>
          {user.role === "it_admin" && <a href="#employees" className="active">Employees</a>}
          {user.role !== "it_admin" && <a href="#dashboard" className={activePage === "dashboard" ? "active" : ""}>Dashboard</a>}
          {isSales && <a href="#customers" className={activePage === "customers" ? "active" : ""}>Customers</a>}
          {isSales && <a href="#orders" className={activePage === "orders" ? "active" : ""}>Customer orders</a>}
        </nav>
        <button className="logout-button" onClick={() => { clearSession(); setUser(null); }}>Sign out</button>
      </aside>
      <main className="main-content">
        <header className="topbar"><div><strong>{user.name}</strong><span>{roleNames[user.role] || user.role}</span></div></header>
        {user.role === "it_admin" && <Employees />}
        {user.role !== "it_admin" && activePage === "dashboard" && <Dashboard />}
        {isSales && activePage === "customers" && <Customers />}
        {isSales && activePage === "orders" && <CustomerOrders />}
      </main>
    </div>
  );
}

/** @param {{ user: any, onChanged: (user: any) => void }} props */
function RequiredPasswordChange({ user, onChanged }) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

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
        <p className="form-help">Your administrator requires a new password before you continue.</p>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={submit}>
          <label htmlFor="old-password">Current password</label>
          <input id="old-password" type="password" value={oldPassword} onChange={(event) => setOldPassword(event.target.value)} required />
          <label htmlFor="required-new-password">New password</label>
          <input id="required-new-password" type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} minLength={8} required />
          <button className="primary-button" type="submit" disabled={busy}>{busy ? "Updating…" : "Continue"}</button>
        </form>
      </section>
    </main>
  );
}