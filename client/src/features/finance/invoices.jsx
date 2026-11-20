import React from 'react'
import { useEffect } from 'react';
import { useState } from 'react';
import { getInvoices } from '../../api/finance';

export const Invoices = () => {

  const [invoices, setInvoices] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    getInvoices()
      .then(setInvoices)
      .catch((err) => setError(err.response?.data?.message || "Failed to load invoices from the server"));
  }, []);

  if (error) return <p>{error}</p>
  return (
    <>
        <section>
          <h1>The Invoices</h1>
          <h2>An overview of financial operations</h2>
        </section>
    </>
  )
}
import { useEffect, useState } from "react";
import { getInvoices, createInvoice } from "../api/invoices";
import { parseApiError } from "../api/errors";
import Payments from "./payments";

const emptyForm = {
  customer_id: "",
  product_id: "",
  sale_id: "",
  unit_price: "",
  quantity: "",
  total: "",
};

const formFields = [
  { name: "customer_id", label: "Customer ID", type: "number" },
  { name: "product_id", label: "Product ID", type: "number" },
  { name: "sale_id", label: "Sale ID", type: "number" },
  { name: "unit_price", label: "Unit price", type: "text", placeholder: "100.00" },
  { name: "quantity", label: "Quantity", type: "number" },
  { name: "total", label: "Total (optional)", type: "text", placeholder: "Calculated if left blank" },
];

// Display helpers only. The backend stays the authority on all money maths.
const toNumber = (value) => Number(value) || 0;
const fmt = (value) => toNumber(value).toFixed(2);
const balanceOf = (invoice) => fmt(toNumber(invoice.total) - toNumber(invoice.amount_paid));

const statusColors = {
  pending: { background: "#fff4d6", color: "#7a5a00" },
  partial: { background: "#dbeafe", color: "#1e40af" },
  paid: { background: "#dcfce7", color: "#166534" },
  void: { background: "#e5e7eb", color: "#4b5563" },
};

function StatusBadge({ status }) {
  const colors = statusColors[status] || statusColors.pending;
  return <span style={{ ...styles.badge, ...colors }}>{status}</span>;
}

export default function Invoices() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [success, setSuccess] = useState("");

  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    let cancelled = false;

    getInvoices()
      .then((data) => {
        if (!cancelled) setInvoices(data);
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
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);
    setSuccess("");

    try {
      const { invoice, message } = await createInvoice({
        customer_id: Number(form.customer_id),
        product_id: Number(form.product_id),
        sale_id: Number(form.sale_id),
        unit_price: form.unit_price,
        quantity: Number(form.quantity),
        total: form.total,
      });

      setInvoices((prev) => [invoice, ...prev]);
      setForm(emptyForm);
      setSuccess(message || "Invoice created");
    } catch (err) {
      setFormError(parseApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  // Called by <Payments /> after a payment is recorded, so the table
  // shows the new amount_paid and status without refetching.
  const handleInvoiceUpdated = (updated) => {
    setInvoices((prev) => prev.map((inv) => (inv.id === updated.id ? updated : inv)));
  };

  const previewTotal = fmt(toNumber(form.unit_price) * toNumber(form.quantity));
  const selectedInvoice = invoices.find((inv) => inv.id === selectedId);

  return (
    <div style={styles.page}>
      <h1 style={styles.h1}>Invoices</h1>

      <section style={styles.section}>
        <h2 style={styles.h2}>Create invoice</h2>

        <form onSubmit={handleSubmit}>
          <div style={styles.grid}>
            {formFields.map((field) => (
              <label key={field.name} style={styles.label}>
                {field.label}
                <input
                  name={field.name}
                  type={field.type}
                  value={form[field.name]}
                  onChange={handleChange}
                  placeholder={field.placeholder}
                  required={field.name !== "total"}
                  min={field.type === "number" ? 1 : undefined}
                  style={{
                    ...styles.input,
                    ...(formError?.fieldErrors[field.name] ? styles.inputError : {}),
                  }}
                />
                {formError?.fieldErrors[field.name] && (
                  <span style={styles.fieldError}>{formError.fieldErrors[field.name]}</span>
                )}
              </label>
            ))}
          </div>

          <p style={styles.hint}>Calculated total: {previewTotal}</p>

          {formError && <p style={styles.error}>{formError.message}</p>}
          {success && <p style={styles.success}>{success}</p>}

          <button type="submit" disabled={submitting} style={styles.primaryButton}>
            {submitting ? "Creating..." : "Create invoice"}
          </button>
        </form>
      </section>

      <section style={styles.section}>
        <h2 style={styles.h2}>All invoices</h2>

        {loading && <p>Loading invoices...</p>}
        {loadError && <p style={styles.error}>{loadError}</p>}
        {!loading && !loadError && invoices.length === 0 && (
          <p>No invoices yet. Create one from an existing sale above.</p>
        )}

        {invoices.length > 0 && (
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Invoice</th>
                  <th style={styles.th}>Sale</th>
                  <th style={styles.th}>Customer</th>
                  <th style={styles.th}>Product</th>
                  <th style={styles.thRight}>Qty</th>
                  <th style={styles.thRight}>Total</th>
                  <th style={styles.thRight}>Paid</th>
                  <th style={styles.thRight}>Balance</th>
                  <th style={styles.th}>Status</th>
                  <th style={styles.th}></th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr
                    key={inv.id}
                    style={inv.id === selectedId ? styles.selectedRow : undefined}
                  >
                    <td style={styles.td}>#{inv.id}</td>
                    <td style={styles.td}>{inv.sale_id}</td>
                    <td style={styles.td}>{inv.customer_id}</td>
                    <td style={styles.td}>{inv.product_id}</td>
                    <td style={styles.tdRight}>{inv.quantity}</td>
                    <td style={styles.tdRight}>{fmt(inv.total)}</td>
                    <td style={styles.tdRight}>{fmt(inv.amount_paid)}</td>
                    <td style={styles.tdRight}>{balanceOf(inv)}</td>
                    <td style={styles.td}>
                      <StatusBadge status={inv.status} />
                    </td>
                    <td style={styles.td}>
                      <button
                        type="button"
                        onClick={() => setSelectedId(inv.id === selectedId ? null : inv.id)}
                        style={styles.linkButton}
                      >
                        {inv.id === selectedId ? "Hide payments" : "View payments"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedInvoice && (
        <section style={styles.section}>
          <Payments invoice={selectedInvoice} onInvoiceUpdated={handleInvoiceUpdated} />
        </section>
      )}
    </div>
  );
}

const styles = {
  page: { maxWidth: 1000, margin: "0 auto", padding: "24px 16px", fontFamily: "system-ui, sans-serif" },
  h1: { fontSize: 28, margin: "0 0 24px" },
  h2: { fontSize: 18, margin: "0 0 12px" },
  section: { marginBottom: 32 },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 },
  label: { display: "flex", flexDirection: "column", gap: 4, fontSize: 14, fontWeight: 500 },
  input: { padding: "8px 10px", border: "1px solid #c4c4c4", borderRadius: 6, fontSize: 14 },
  inputError: { borderColor: "#dc2626" },
  fieldError: { color: "#dc2626", fontSize: 12, fontWeight: 400 },
  hint: { fontSize: 13, color: "#555", margin: "12px 0" },
  error: { color: "#dc2626", margin: "8px 0" },
  success: { color: "#166534", margin: "8px 0" },
  primaryButton: {
    padding: "9px 16px",
    background: "#1d4ed8",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    fontSize: 14,
    cursor: "pointer",
  },
  linkButton: {
    background: "none",
    border: "none",
    color: "#1d4ed8",
    cursor: "pointer",
    fontSize: 14,
    padding: 0,
  },
  tableWrap: { overflowX: "auto" },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 14 },
  th: { textAlign: "left", padding: "8px 10px", borderBottom: "2px solid #e5e7eb", whiteSpace: "nowrap" },
  thRight: { textAlign: "right", padding: "8px 10px", borderBottom: "2px solid #e5e7eb" },
  td: { padding: "8px 10px", borderBottom: "1px solid #eee", whiteSpace: "nowrap" },
  tdRight: { padding: "8px 10px", borderBottom: "1px solid #eee", textAlign: "right" },
  selectedRow: { background: "#f3f6ff" },
  badge: { padding: "2px 8px", borderRadius: 999, fontSize: 12, fontWeight: 500 },
};