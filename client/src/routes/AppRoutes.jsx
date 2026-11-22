import { useState } from "react";
import Login, { roleNames } from "../features/auth/login";
import History from "../features/supply/history";
import RegSuppliers from "../features/supply/reg_suppliers";
import SupplyOrders from "../features/supply/supply_orders";
import Customers from "../features/sales/customers";
import CustomerOrders from "../features/sales/customer_orders";
import Employees from "../features/admin/employees";
import Dashboard from "../features/admin/dashboard";
import Inventory from "../features/inventory/inventory";
import Invoices from "../features/finance/invoices";
import AuditDashboard from "../features/auditor/audit_dashboard";
import AddProduct from "../features/wearhouse/add_product";
import Deliveries from "../features/wearhouse/deliveries";
import Reports from "../features/wearhouse/reports";
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
  const [activePage, setActivePage] = useState("dashboard");

  if (!user) return <Login onAuthenticated={setUser} />;

  if (user.must_change_password) {
    return (
      <RequiredPasswordChange
        user={user}
        onChanged={(updatedUser) => setUser(updatedUser)}
      />
    );
  }

  const isOperationsDirector = user.role === "operations_director";
  const isWarehouseUser = ["store_worker", "operations_director"].includes(user.role);

  let navigation;
  if (user.role === "it_admin") {
    navigation = [{ href: "#employees", label: "Employees", page: "employees" }];
  } else if (user.role === "procurement_officer") {
    navigation = [
      { href: "#suppliers", label: "Suppliers", page: "suppliers" },
      { href: "#supply-orders", label: "Supply Orders", page: "supply-orders" },
      { href: "#supply-history", label: "Supply History", page: "supply-history" },
    ];
  } else if (user.role === "sales_officer") {
    navigation = [
      { href: "#customers", label: "Customers", page: "customers" },
      { href: "#customer-orders", label: "Customer Orders", page: "customer-orders" },
    ];
  } else if (user.role === "finance_officer") {
    navigation = [{ href: "#invoices", label: "Invoices", page: "invoices" }];
  } else if (user.role === "auditor") {
    navigation = [{ href: "#audit", label: "Audit Logs", page: "audit" }];
  } else if (isWarehouseUser) {
    navigation = [
      ...(isOperationsDirector
        ? [{ href: "#dashboard", label: "Dashboard", page: "dashboard" }]
        : []),
      { href: "#warehouse-products", label: "Products", page: "warehouse-products" },
      { href: "#warehouse-deliveries", label: "Deliveries", page: "warehouse-deliveries" },
      { href: "#warehouse-reports", label: "Reports", page: "warehouse-reports" },
    ];
  } else {
    navigation = [{ href: "#dashboard", label: "Dashboard", page: "dashboard" }];
  }
  const selectedPage = navigation.some((item) => item.page === activePage)
    ? activePage
    : navigation[0].page;

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
            <a
              key={item.href}
              href={item.href}
              className={selectedPage === item.page ? "active" : ""}
              onClick={() => setActivePage(item.page)}
            >
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
              className={selectedPage === item.page ? "active" : ""}
              onClick={() => {
                setActivePage(item.page);
                setMobileMenuOpen(false);
              }}
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
        {selectedPage === "employees" ? <Employees />
          : selectedPage === "suppliers" ? <RegSuppliers />
            : selectedPage === "supply-orders" ? <SupplyOrders />
              : selectedPage === "supply-history" ? <History />
                : selectedPage === "customers" ? <Customers />
                  : selectedPage === "customer-orders" ? <CustomerOrders />
                    : selectedPage === "inventory" ? <Inventory />
                      : selectedPage === "invoices" ? <Invoices />
                        : selectedPage === "audit" ? <AuditDashboard />
                          : selectedPage === "warehouse-products" ? <AddProduct />
                            : selectedPage === "warehouse-deliveries" ? <Deliveries />
                              : selectedPage === "warehouse-reports" ? <Reports />
                                : <Dashboard />}
      </main>
    </div>
  );
}

/** @param {{ user: AuthUser, onChanged: (user: AuthUser) => void }} props */
function RequiredPasswordChange({ user, onChanged }) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      await changePassword(oldPassword, newPassword, confirmPassword);
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
          <div className="password-field">
            <input
              id="old-password"
              type={showOldPassword ? "text" : "password"}
              value={oldPassword}
              onChange={(event) => setOldPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
            <button className="password-toggle" type="button" aria-label={showOldPassword ? "Hide current password" : "Show current password"} aria-pressed={showOldPassword} onClick={() => setShowOldPassword((visible) => !visible)}>
              {showOldPassword ? "Hide" : "Show"}
            </button>
          </div>

          <label htmlFor="required-new-password">New password</label>
          <div className="password-field">
            <input
              id="required-new-password"
              type={showNewPassword ? "text" : "password"}
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              autoComplete="new-password"
              minLength={8}
              required
            />
            <button className="password-toggle" type="button" aria-label={showNewPassword ? "Hide new password" : "Show new password"} aria-pressed={showNewPassword} onClick={() => setShowNewPassword((visible) => !visible)}>
              {showNewPassword ? "Hide" : "Show"}
            </button>
          </div>

          <label htmlFor="required-confirm-password">Confirm new password</label>
          <div className="password-field">
            <input
              id="required-confirm-password"
              type={showConfirmPassword ? "text" : "password"}
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              autoComplete="new-password"
              minLength={8}
              required
            />
            <button className="password-toggle" type="button" aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"} aria-pressed={showConfirmPassword} onClick={() => setShowConfirmPassword((visible) => !visible)}>
              {showConfirmPassword ? "Hide" : "Show"}
            </button>
          </div>

          <button className="primary-button" type="submit" disabled={busy}>
            {busy ? "Updating…" : "Continue"}
          </button>
        </form>
      </section>
    </main>
  );
}
