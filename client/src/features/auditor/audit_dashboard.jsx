import { useEffect, useState } from "react";
import { verifyAuditChain } from "../../api/audit";
import "./audit_dashboard.css";

export default function AuditDashboard() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function verify() {
    setLoading(true);
    setError("");
    try {
      setResult(await verifyAuditChain());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to verify the audit log chain.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    verify();
  }, []);

  return (
    <div className="dashboard audit-dashboard">
      <div className="page-heading">
        <div>
          <h1>Audit Logs</h1>
          <p>Verify the integrity of the recorded audit chain.</p>
        </div>
        <button className="primary-button" type="button" onClick={verify} disabled={loading}>
          {loading ? "Verifying..." : "Verify chain"}
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <h3>Chain verification</h3>
              <p>Current audit log status</p>
            </div>
            <span className={`status-badge ${result.valid ? "completed" : "low"}`}>
              {result.valid ? "Valid" : "Invalid"}
            </span>
          </div>
          <div className="audit-verification-content">
            <div className={`audit-verification-icon ${result.valid ? "" : "invalid"}`} aria-hidden="true">
              {result.valid ? "✓" : "!"}
            </div>
            <div>
              <strong>{result.valid ? "Audit chain is intact" : "Audit chain integrity check failed"}</strong>
              {result.valid ? (
                <p>All recorded audit entries passed verification.</p>
              ) : result.broken_at != null ? (
                <p>First broken audit record: #{result.broken_at}</p>
              ) : (
                <p>The chain contains one or more invalid records.</p>
              )}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
