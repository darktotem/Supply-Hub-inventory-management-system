import { useState } from "react";
import {
  login,
  saveSession,
  setNewPassword as setNewPasswordRequest,
  verifyRecoveryCode,
} from "../../api/auth";
import "./login.css";
const roleNames = {
  operations_director: "Operations Director",
  it_admin: "IT Administrator",
  procurement_officer: "Procurement Officer",
  store_worker: "Store / Warehouse",
  sales_officer: "Sales Officer",
  finance_officer: "Finance Officer",
  auditor: "Auditor",
};

/** @param {{ onAuthenticated: (user: any) => void }} props */
export default function Login({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [recoveryCode, setRecoveryCode] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  function resetMessage() {
    setError("");
    setNotice("");
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleLogin(event) {
    event.preventDefault();
    resetMessage();
    setBusy(true);
    try {
      const data = await login(username.trim(), password);
      saveSession(data.token, data.user);
      onAuthenticated(data.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed");
    } finally {
      setBusy(false);
    }
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleVerifyCode(event) {
    event.preventDefault();
    resetMessage();
    setBusy(true);
    try {
      const data = await verifyRecoveryCode(username.trim(), recoveryCode);
      setResetToken(data.reset_token);
      setMode("reset");
      setNotice("Recovery code accepted. Choose a new password.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Recovery verification failed");
    } finally {
      setBusy(false);
    }
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function handleReset(event) {
    event.preventDefault();
    resetMessage();
    setBusy(true);
    try {
      const data = await setNewPasswordRequest(resetToken, newPassword, confirmPassword);
      setPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setMode("login");
      setNotice(data.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Password update failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="auth-title">
        <div className="brand-mark" aria-hidden="true">SH</div>
        <p className="eyebrow">Supply Hub</p>
        <h1 id="auth-title">
          {mode === "login" && "Sign in"}
          {mode === "recovery" && "Account recovery"}
          {mode === "reset" && "Set a new password"}
        </h1>

        {error && <div className="alert alert-error" role="alert">{error}</div>}
        {notice && <div className="alert alert-success" role="status">{notice}</div>}

        {mode === "login" && (
          <form onSubmit={handleLogin}>
            <label htmlFor="username">Username</label>
            <input id="username" value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" required />
            <label htmlFor="password">Password</label>
            <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required />
            <button className="primary-button" type="submit" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
            <button className="text-button" type="button" onClick={() => { resetMessage(); setMode("recovery"); }}>Forgot password?</button>
          </form>
        )}

        {mode === "recovery" && (
          <form onSubmit={handleVerifyCode}>
            <p className="form-help">Enter the username and recovery code provided by IT.</p>
            <label htmlFor="recovery-username">Username</label>
            <input id="recovery-username" value={username} onChange={(e) => setUsername(e.target.value)} required />
            <label htmlFor="recovery-code">Recovery code</label>
            <input id="recovery-code" value={recoveryCode} onChange={(e) => setRecoveryCode(e.target.value.toUpperCase())} placeholder="A1B2-C3D4-E5F6" required />
            <button className="primary-button" type="submit" disabled={busy}>{busy ? "Checking…" : "Continue"}</button>
            <button className="text-button" type="button" onClick={() => { resetMessage(); setMode("login"); }}>Back to sign in</button>
          </form>
        )}

        {mode === "reset" && (
          <form onSubmit={handleReset}>
            <label htmlFor="new-password">New password</label>
            <input id="new-password" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} autoComplete="new-password" minLength={8} required />
            <label htmlFor="confirm-password">Confirm password</label>
            <input id="confirm-password" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} autoComplete="new-password" minLength={8} required />
            <button className="primary-button" type="submit" disabled={busy}>{busy ? "Updating…" : "Update password"}</button>
          </form>
        )}
      </section>
    </main>
  );
}

export { roleNames };
