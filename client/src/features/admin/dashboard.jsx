import { useEffect, useState } from "react";
import { getInventory } from "../../api/inventory";
import { getSuppliers } from "../../api/supply";
import "./dashboard.css";


function Dashboard() {
  const [inventory, setInventory] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    Promise.all([getInventory(), getSuppliers()])
      .then(([inventoryResult, supplierResult]) => {
        if (!active) return;
        setInventory(Array.isArray(inventoryResult) ? inventoryResult : []);
        setSuppliers(Array.isArray(supplierResult) ? supplierResult : []);
      })
      .catch((requestError) => {
        if (active) setError(requestError instanceof Error ? requestError.message : "Unable to load dashboard data.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  }, []);

  const lowStockItems = inventory
    .filter((item) => Number(item.quantity) <= Number(item.threshold))
    .sort((a, b) => Number(a.quantity) - Number(b.quantity));
  const stockValue = inventory.reduce((total, item) => {
    const quantity = Number(item.quantity) || 0;
    const price = Number(item.unit_price ?? item.price) || 0;
    return total + quantity * price;
  }, 0);

  const summaryCards = [
    { title: "Total Products", value: loading ? "—" : inventory.length.toLocaleString(), detail: "Inventory records", icon: "▦", tone: "blue" },
    { title: "Stock Value", value: loading ? "—" : `KES ${stockValue.toLocaleString()}`, detail: "Estimated inventory value", icon: "◈", tone: "green" },
    { title: "Low Stock Items", value: loading ? "—" : lowStockItems.length.toLocaleString(), detail: lowStockItems.length ? "Requires replenishment" : "No restocking alerts", icon: "⚠", tone: "amber" },
    { title: "Active Suppliers", value: loading ? "—" : suppliers.length.toLocaleString(), detail: "Registered suppliers", icon: "♧", tone: "violet" },
  ];

  return (
    <div className="dashboard operations-dashboard">
      <div className="operations-heading">
        <div>
          <p className="operations-eyebrow">Operations overview</p>
          <h1>Director Dashboard</h1>
          <p>Monitor inventory health and restocking priorities.</p>
        </div>
        <div className="operations-status">
          <span aria-hidden="true"></span>
          Live operations
        </div>
      </div>

      {error && <div className="operations-error" role="alert">{error}</div>}

      <div className="summary-grid">
        {summaryCards.map((card) => (
          <article className="summary-card" key={card.title}>
            <div className="summary-card-top">
              <div>
                <span className="summary-label">{card.title}</span>
                <strong>{card.value}</strong>
              </div>
              <span className={`summary-icon summary-icon-${card.tone}`} aria-hidden="true">{card.icon}</span>
            </div>
            <p>{card.detail}</p>
          </article>
        ))}
      </div>

      <div className="dashboard-grid">
        <section className="dashboard-panel low-stock-panel">
          <div className="panel-heading">
            <div>
              <h3>Low stock alerts</h3>
              <p>Items at or below their reorder threshold</p>
            </div>
            <span className="alert-count">{loading ? "Loading" : `${lowStockItems.length} alerts`}</span>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>In stock</th>
                  <th>Threshold</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {!loading && lowStockItems.length === 0 && (
                  <tr><td colSpan="5" className="empty-table">No low-stock items found.</td></tr>
                )}
                {lowStockItems.slice(0, 8).map((item) => (
                  <tr key={item.id ?? item.name}>
                    <td><strong className="product-name">{item.name}</strong></td>
                    <td>{item.category || "Uncategorised"}</td>
                    <td><strong>{item.quantity}</strong></td>
                    <td>{item.threshold}</td>
                    <td><span className="status-badge low">Low stock</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="dashboard-panel operations-health">
          <div className="panel-heading">
            <div>
              <h3>Inventory health</h3>
              <p>Current stock distribution</p>
            </div>
          </div>
          <div className="health-content">
            <div className="health-ring" style={{ "--health": `${inventory.length ? Math.round(((inventory.length - lowStockItems.length) / inventory.length) * 100) : 100}%` }}>
              <div><strong>{loading ? "—" : `${inventory.length ? Math.round(((inventory.length - lowStockItems.length) / inventory.length) * 100) : 100}%`}</strong><span>healthy</span></div>
            </div>
            <div className="health-stats">
              <div><span className="health-dot healthy"></span><p><strong>{loading ? "—" : inventory.length - lowStockItems.length}</strong><small>Well stocked</small></p></div>
              <div><span className="health-dot warning"></span><p><strong>{loading ? "—" : lowStockItems.length}</strong><small>Low stock</small></p></div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default Dashboard