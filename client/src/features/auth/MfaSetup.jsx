import { useState } from "react";
import { QRCodeSVG } from "qrcode.react";

/** @typedef {{ secret: string, otpauth_uri: string }} MfaSetupData */
import { setupMfa, enableMfa } from "../../api/auth";

/** @param {{ onEnabled?: (user: import("../../api/auth").AuthUser) => void }} props */
export default function MfaSetup({ onEnabled }) {
  const [setup, setSetup] = useState(/** @type {MfaSetupData | null} */ (null));
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  async function start() {
    setError("");
    try {
      setSetup(await setupMfa());
    } catch (err) {
      setError(err instanceof Error ? err.message : "MFA setup failed");
    }
  }

  /** @param {import("react").FormEvent<HTMLFormElement>} event */
  async function confirm(event) {
    event.preventDefault();
    setError("");
    try {
      const data = await enableMfa(code.trim());
      setSetup(null);
      setDone(true);
      onEnabled?.(data.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "MFA verification failed");
    }
  }

  if (done) return <p>Two-step verification is on.</p>;

  return (
    <section>
      <h2>Two-step verification</h2>
      {error && <div className="alert alert-error" role="alert">{error}</div>}
      {!setup ? (
        <button className="primary-button" type="button" onClick={start}>Set up authenticator app</button>
      ) : (
        <form onSubmit={confirm}>
          <p className="form-help">Scan this QR code with Google Authenticator, then enter the 6-digit code it shows.</p>
          <QRCodeSVG value={setup.otpauth_uri} size={180} />
          <p className="form-help">Can't scan? Enter this key manually: <code>{setup.secret}</code></p>
          <label htmlFor="mfa-setup-code">Code</label>
          <input id="mfa-setup-code" value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))} inputMode="numeric" maxLength={6} required />
          <button className="primary-button" type="submit" disabled={code.length !== 6}>Turn on</button>
        </form>
      )}
    </section>
  );
}