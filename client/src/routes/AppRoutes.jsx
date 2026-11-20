
import { useState } from "react";
import Login, { roleNames } from "../features/auth/login";
import Employees from "../features/admin/employees";
import Dashboard from "../features/admin/dashboard";
import { Navbar } from "../components/Navbar";
import {
  changePassword,
  clearSession,
  getSavedUser,
  getSavedToken,
} from "../api/auth";

export default function AppRoutes() {
  const [user, setUser] = useState(() => {
    const savedUser = getSavedUser();
    return getSavedToken() && savedUser ? savedUser : null;
  });

  if (!user) return <Login onAuthenticated={setUser} />;

  if (user.must_change_password) {
    return (
      <RequiredPasswordChange
        user={user}
        onChanged={(updatedUser) => setUser(updatedUser)}
      />
    );
  }

  const links =
    user.role === "it_admin"
      ? [{ label: "Employees", path: "#employees" }]
      : [{ label: "Dashboard", path: "#dashboard" }];

  return (
    <div className="flex min-h-screen w-full bg-[#f4f6fb]">
      <Navbar links={links} />

      <main className="min-w-0 flex-1">
        <header className="flex h-[76px] items-center justify-between border-b border-slate-200 bg-white px-8">
          <div>
            <p className="font-semibold text-slate-800">{user.name}</p>
            <p className="text-sm capitalize text-slate-500">
              {roleNames[user.role] || user.role}
            </p>
          </div>

          <button
            onClick={() => {
              clearSession();
              setUser(null);
            }}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
          >
            Sign out
          </button>
        </header>

        <div className="p-8">
          {user.role === "it_admin" ? <Employees /> : <Dashboard />}
        </div>
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
      setError(
        err instanceof Error ? err.message : "Unable to change password"
      );
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
