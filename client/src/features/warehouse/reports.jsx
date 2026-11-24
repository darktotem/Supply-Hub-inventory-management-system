import { useEffect, useState } from "react";
import {
  getWarehouseReport,
  getWarehouseReportHistory,
  saveWarehouseReport,
} from "../../api/warehouse";
import "./warehouse.css";

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat("en-KE", {
        dateStyle: "medium",
        timeStyle: "short",
      }).format(date);
}

function Reports({ readOnly = false }) {
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadReports() {
      const [currentResult, historyResult] = await Promise.allSettled([
        getWarehouseReport(),
        getWarehouseReportHistory(),
      ]);

      if (cancelled) return;

      if (currentResult.status === "fulfilled") {
        setReport(currentResult.value);
      } else {
        setError(
          currentResult.reason instanceof Error
            ? currentResult.reason.message
            : "Could not load the inventory report."
        );
      }

      if (historyResult.status === "fulfilled") {
        setHistory(Array.isArray(historyResult.value) ? historyResult.value : []);
      } else {
        const message = historyResult.reason instanceof Error
          ? historyResult.reason.message
          : "Could not load saved report history.";
        setError((previous) => previous ? `${previous} ${message}` : message);
      }

      setLoading(false);
    }

    loadReports();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleSave() {
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const savedReport = await saveWarehouseReport();
      setHistory((previous) => [savedReport, ...previous]);
      setReport(savedReport);
      setSuccess("Inventory report saved successfully.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save the report.");
    } finally {
      setSaving(false);
    }
  }

  const inventory = Array.isArray(report?.inventory) ? report.inventory : [];
  const lowStockItems = inventory.filter(
    (item) => Number(item.quantity) <= Number(item.threshold)
  );

  return (
    <section className="warehouse-page" aria-labelledby="warehouse-reports-title">
      <header className="warehouse-heading">
        <div>
          <p className="warehouse-eyebrow">Warehouse / Insights</p>
          <h1 id="warehouse-reports-title">Inventory reports</h1>
          <p>Review current inventory health and save point-in-time reports.</p>
        </div>
        {!readOnly && <button
          className="warehouse-primary-button"
          type="button"
          onClick={handleSave}
          disabled={saving || loading || !report}
        >
          {saving ? "Saving report…" : "Save current report"}
        </button>}
      </header>

      {error && <div className="warehouse-alert warehouse-alert-error" role="alert">{error}</div>}
      {success && <div className="warehouse-alert warehouse-alert-success" role="status">{success}</div>}

      {loading ? (
        <section className="warehouse-panel">
          <p className="warehouse-empty-state">Preparing inventory report…</p>
        </section>
      ) : report ? (
        <>
          <p className="warehouse-report-timestamp">
            Current inventory snapshot · Updated {formatDate(report.generated_at)}
          </p>
          <div className="warehouse-stats">
            <article className="warehouse-stat">
              <span>Products tracked</span>
              <strong>{report.total_products ?? inventory.length}</strong>
              <small>Distinct inventory products</small>
            </article>
            <article className="warehouse-stat">
              <span>Total units</span>
              <strong>{report.total_quantity ?? inventory.reduce((sum, item) => sum + Number(item.quantity || 0), 0)}</strong>
              <small>Across all product categories</small>
            </article>
            <article className="warehouse-stat warehouse-stat-warning">
              <span>Low stock products</span>
              <strong>{report.low_stock_count ?? lowStockItems.length}</strong>
              <small>At or below reorder threshold</small>
            </article>
          </div>

          <section className="warehouse-panel">
            <div className="warehouse-panel-heading">
              <div>
                <h2>Inventory breakdown</h2>
                <p>Products at or below their threshold are highlighted.</p>
              </div>
            </div>
            {inventory.length === 0 ? (
              <p className="warehouse-empty-state">There are no products in inventory yet.</p>
            ) : (
              <div className="warehouse-table-scroll">
                <table className="warehouse-table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Category</th>
                      <th>Quantity</th>
                      <th>Threshold</th>
                      <th>Unit price</th>
                      <th>Stock health</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inventory.map((item) => {
                      const low = Number(item.quantity) <= Number(item.threshold);
                      return (
                        <tr key={item.id}>
                          <td><strong>{item.product_name}</strong></td>
                          <td>{item.category}</td>
                          <td>{item.quantity}</td>
                          <td>{item.threshold}</td>
                          <td>
                            {new Intl.NumberFormat("en-KE", {
                              style: "currency",
                              currency: "KES",
                              maximumFractionDigits: 2,
                            }).format(Number(item.price) || 0)}
                          </td>
                          <td>
                            <span className={`warehouse-badge ${low ? "warehouse-badge-warning" : "warehouse-badge-success"}`}>
                              {low ? "Restock needed" : "Healthy"}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      ) : (
        <section className="warehouse-panel">
          <p className="warehouse-empty-state">The inventory report is unavailable.</p>
        </section>
      )}

      <section className="warehouse-panel warehouse-history-panel">
        <div className="warehouse-panel-heading">
          <div>
            <h2>Saved reports</h2>
            <p>Previously saved inventory snapshots.</p>
          </div>
        </div>
        {history.length === 0 ? (
          <p className="warehouse-empty-state">No reports have been saved yet.</p>
        ) : (
          <div className="warehouse-table-scroll">
            <table className="warehouse-table">
              <thead>
                <tr>
                  <th>Report</th>
                  <th>Generated</th>
                  <th>Products</th>
                  <th>Total units</th>
                  <th>Low stock</th>
                </tr>
              </thead>
              <tbody>
                {history.map((savedReport) => (
                  <tr key={savedReport.id}>
                    <td><strong>Inventory #{savedReport.id}</strong></td>
                    <td>{formatDate(savedReport.generated_at)}</td>
                    <td>{savedReport.total_products}</td>
                    <td>{savedReport.total_quantity}</td>
                    <td>{savedReport.low_stock_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  );
}

export default Reports;