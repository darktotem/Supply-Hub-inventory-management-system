
import { useEffect, useState } from "react";
import { getPayments, addPayment } from "../../api/finance";
import { parseApiError } from "../../api/errors";

const methods = [
  { value: "cash", label: "Cash" },
  { value: "mpesa", label: "M-Pesa" },
  { value: "bank", label: "Bank" },
  { value: "card", label: "Card" },
];

const methodLabel = (value) => methods.find((m) => m.value === value)?.label || value;

const toNumber = (value) => Number(value) || 0;
const fmt = (value) => toNumber(value).toFixed(2);

export default function Payments({ invoice, onInvoiceUpdated, readOnly = false }) {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState("cash");
  const [reference, setReference] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [success, setSuccess] = useState("");

  const balance = fmt(toNumber(invoice.total) - toNumber(invoice.amount_paid));
  const closed = invoice.status === "paid" || invoice.status === "void";

  // Reload whenever a different invoice is selected
  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    setLoadError(null);
    setFormError(null);
    setSuccess("");
    setAmount("");
    setReference("");

    getPayments(invoice.id)
      .then((data) => {
        if (!cancelled) setPayments(data);
      })
      .catch((err) => {
        if (!cancelled) setLoadError(parseApiError(err).message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [invoice.id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setSuccess("");

    try {
      const result = await addPayment(invoice.id, {
        amount,
        method,
        reference: reference.trim(),
      });

      setPayments((prev) => [...prev, result.payment]);
      onInvoiceUpdated?.(result.invoice); // refresh amount_paid and status in the parent
      setAmount("");
      setReference("");
      setSuccess(result.message || "Payment recorded");
    } catch (err) {
      setFormError(parseApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h2 style={styles.h2}>Payments for invoice #{invoice.id}</h2>

      <div style={styles.summary}>
        <div>
          <span style={styles.summaryLabel}>Total</span>
          <strong>{fmt(invoice.total)}</strong>
        </div>
        <div>
          <span style={styles.summaryLabel}>Paid</span>
          <strong>{fmt(invoice.amount_paid)}</strong>
        </div>
        <div>
          <span style={styles.summaryLabel}>Balance due</span>
          <strong>{balance}</strong>
        </div>
        <div>
          <span style={styles.summaryLabel}>Status</span>
          <strong>{invoice.status}</strong>
        </div>
      </div>

      {readOnly ? (
        <p style={styles.notice}>Payment entry is restricted to finance officers.</p>
      ) : closed ? (
        <p style={styles.notice}>
          This invoice is {invoice.status}, so it can't take more payments.
        </p>
      ) : (
        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>
            Amount
            <input
              type="text"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="50.00"
              required
              style={{
                ...styles.input,
                ...(formError?.fieldErrors.amount ? styles.inputError : {}),
              }}
            />
            {formError?.fieldErrors.amount && (
              <span style={styles.fieldError}>{formError.fieldErrors.amount}</span>
            )}
          </label>

          <label style={styles.label}>
            Method
            <select value={method} onChange={(e) => setMethod(e.target.value)} style={styles.input}>
              {methods.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </label>

          <label style={styles.label}>
            Reference (optional)
            <input
              type="text"
              value={reference}
              onChange={(e) => setReference(e.target.value)}
              placeholder="M-Pesa code, receipt no."
              style={{
                ...styles.input,
                ...(formError?.fieldErrors.reference ? styles.inputError : {}),
              }}
            />
            {formError?.fieldErrors.reference && (
              <span style={styles.fieldError}>{formError.fieldErrors.reference}</span>
            )}
          </label>

          <div style={styles.actions}>
            <button type="submit" disabled={submitting} style={styles.primaryButton}>
              {submitting ? "Saving..." : "Record payment"}
            </button>
            <button
              type="button"
              onClick={() => setAmount(balance)}
              disabled={submitting || toNumber(balance) <= 0}
              style={styles.secondaryButton}
            >
              Fill balance ({balance})
            </button>
          </div>
        </form>
      )}

      {formError && <p style={styles.error}>{formError.message}</p>}
      {success && <p style={styles.success}>{success}</p>}

      <h3 style={styles.h3}>Payment history</h3>

      {loading && <p>Loading payments...</p>}
      {loadError && <p style={styles.error}>{loadError}</p>}
      {!loading && !loadError && payments.length === 0 && (
        <p>No payments recorded for this invoice yet.</p>
      )}

      {payments.length > 0 && (
        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Payment</th>
                <th style={styles.thRight}>Amount</th>
                <th style={styles.th}>Method</th>
                <th style={styles.th}>Reference</th>
                <th style={styles.th}>Date</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id}>
                  <td style={styles.td}>#{p.id}</td>
                  <td style={styles.tdRight}>{fmt(p.amount)}</td>
                  <td style={styles.td}>{methodLabel(p.method)}</td>
                  <td style={styles.td}>{p.reference || "-"}</td>
                  <td style={styles.td}>
                    {p.created_at ? new Date(p.created_at).toLocaleString() : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const styles = {
  h2: { fontSize: 18, margin: "0 0 12px" },
  h3: { fontSize: 16, margin: "24px 0 8px" },
  summary: {
    display: "flex",
    flexWrap: "wrap",
    gap: 24,
    padding: "12px 16px",
    background: "#f6f7f9",
    borderRadius: 8,
    marginBottom: 16,
  },
  summaryLabel: { display: "block", fontSize: 12, color: "#555" },
  notice: { padding: "10px 12px", background: "#f3f4f6", borderRadius: 6 },
  form: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 },
  label: { display: "flex", flexDirection: "column", gap: 4, fontSize: 14, fontWeight: 500 },
  input: { padding: "8px 10px", border: "1px solid #c4c4c4", borderRadius: 6, fontSize: 14 },
  inputError: { borderColor: "#dc2626" },
  fieldError: { color: "#dc2626", fontSize: 12, fontWeight: 400 },
  actions: { display: "flex", gap: 8, alignItems: "flex-end", gridColumn: "1 / -1" },
  primaryButton: {
    padding: "9px 16px",
    background: "#1d4ed8",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    fontSize: 14,
    cursor: "pointer",
  },
  secondaryButton: {
    padding: "9px 16px",
    background: "#fff",
    color: "#1d4ed8",
    border: "1px solid #1d4ed8",
    borderRadius: 6,
    fontSize: 14,
    cursor: "pointer",
  },
  error: { color: "#dc2626", margin: "8px 0" },
  success: { color: "#166534", margin: "8px 0" },
  tableWrap: { overflowX: "auto" },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 14 },
  th: { textAlign: "left", padding: "8px 10px", borderBottom: "2px solid #e5e7eb", whiteSpace: "nowrap" },
  thRight: { textAlign: "right", padding: "8px 10px", borderBottom: "2px solid #e5e7eb" },
  td: { padding: "8px 10px", borderBottom: "1px solid #eee", whiteSpace: "nowrap" },
  tdRight: { padding: "8px 10px", borderBottom: "1px solid #eee", textAlign: "right" },
};