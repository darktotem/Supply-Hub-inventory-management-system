// @ts-nocheck
import { useEffect, useState } from "react";
import {
  getCustomers,
  getProducts,
  getOrders,
  createOrder,
  cancelOrder,
  fulfilOrder,
} from "../../api/sales";
import "./sales.css";

const PAGE_SIZE = 8;

// Which color each status uses (the colors are defined in sales.css)
const statusColors = {
  pending: "orders-orange",
  fulfilled: "orders-green",
  cancelled: "orders-red",
};

// Turns "2026-11-16T09:30:00" into "16 Nov 2026"
function formatDate(text) {
  return new Date(text).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function CustomerOrders() {
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  // New order form
  const [showForm, setShowForm] = useState(false);
  const [customerId, setCustomerId] = useState("");
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState(1);

  // Filters, sorting and pages
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [page, setPage] = useState(1);

  // Load everything when the page opens
  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setCustomers(await getCustomers());
      setProducts(await getProducts());
      setOrders(await getOrders());
    } catch (err) {
      setMessage(err.message);
    }
    setLoading(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (customerId === "" || productId === "") {
      setMessage("Please choose a customer and a product.");
      return;
    }

    try {
      await createOrder(Number(customerId), Number(productId), Number(quantity));
      setCustomerId("");
      setProductId("");
      setQuantity(1);
      setMessage("");
      setShowForm(false);
      loadData();
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function handleCancel(id) {
    try {
      await cancelOrder(id);
      setMessage("");
      loadData();
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function handleFulfil(id) {
    try {
      await fulfilOrder(id);
      setMessage("");
      loadData();
    } catch (err) {
      setMessage(err.message);
    }
  }

  if (loading) {
    return <p>Loading orders...</p>;
  }

  // ----- Numbers for the four cards -----
  const total = orders.length;
  const pendingCount = orders.filter((o) => o.status === "pending").length;
  const fulfilledCount = orders.filter((o) => o.status === "fulfilled").length;
  const cancelledCount = orders.filter((o) => o.status === "cancelled").length;

  function percent(count) {
    if (total === 0) return 0;
    return Math.round((count / total) * 100);
  }

  const stats = [
    { label: "Total Orders", count: total, icon: "🛍️", color: "orders-purple", note: "All orders" },
    { label: "Pending", count: pendingCount, icon: "⏳", color: "orders-orange", note: percent(pendingCount) + "% of orders" },
    { label: "Fulfilled", count: fulfilledCount, icon: "✅", color: "orders-green", note: percent(fulfilledCount) + "% of orders" },
    { label: "Cancelled", count: cancelledCount, icon: "🚫", color: "orders-red", note: percent(cancelledCount) + "% of orders" },
  ];

  // ----- Search, filter and sort -----
  const visible = orders.filter((o) => {
    const text = (o.customer_name + " " + o.product_name).toLowerCase();
    const matchesSearch = text.includes(search.toLowerCase());
    const matchesStatus = statusFilter === "all" || o.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  if (sortBy === "newest") visible.sort((a, b) => b.id - a.id);
  if (sortBy === "oldest") visible.sort((a, b) => a.id - b.id);
  if (sortBy === "amount") visible.sort((a, b) => b.total_price - a.total_price);

  // ----- Pages -----
  const totalPages = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const pageOrders = visible.slice(startIndex, startIndex + PAGE_SIZE);
  const showingFrom = visible.length === 0 ? 0 : startIndex + 1;
  const showingTo = startIndex + pageOrders.length;
  const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1);

  // ----- Export the filtered orders as a CSV file -----
  function exportCsv() {
    const lines = ["Order ID,Customer,Product,Quantity,Amount (KES),Date,Status"];

    visible.forEach((o) => {
      lines.push([
        "ORD-" + o.id,
        '"' + o.customer_name + '"',
        '"' + o.product_name + '"',
        o.quantity,
        o.total_price,
        formatDate(o.date_of_sale),
        o.status,
      ].join(","));
    });

    const file = new Blob([lines.join("\n")], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(file);
    link.download = "customer-orders.csv";
    link.click();
  }

  return (
    <div className="orders-page">
      <div className="orders-header">
        <div>
          <h1>Orders</h1>
          <p className="orders-subtitle">Manage and track all customer orders</p>
        </div>
        <div className="orders-header-buttons">
          <button className="orders-btn orders-btn-light" onClick={exportCsv}>
            ⬇ Export CSV
          </button>
          <button className="orders-btn orders-btn-primary" onClick={() => setShowForm(!showForm)}>
            + New Order
          </button>
        </div>
      </div>

      {message && <p className="orders-message">{message}</p>}

      {showForm && (
        <form className="orders-form" onSubmit={handleSubmit}>
          <label>
            Customer
            <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
              <option value="">Select a customer</option>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.customer_name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Product
            <select value={productId} onChange={(e) => setProductId(e.target.value)}>
              <option value="">Select a product</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.product_name} - KES {p.price} ({p.quantity} in stock)
                </option>
              ))}
            </select>
          </label>

          <label>
            Quantity
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
          </label>

          <button className="orders-btn orders-btn-primary" type="submit">
            Create order
          </button>
        </form>
      )}

      <div className="orders-stats">
        {stats.map((s) => (
          <div key={s.label} className={"orders-stat " + s.color}>
            <div className="orders-stat-top">
              <span className="orders-icon">{s.icon}</span>
              {s.label}
            </div>
            <div className="orders-count">{s.count}</div>
            <span className="orders-note">{s.note}</span>
          </div>
        ))}
      </div>

      <div className="orders-filters">
        <input
          className="orders-search"
          placeholder="Search customer or product..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />

        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
        >
          <option value="all">All statuses</option>
          <option value="pending">Pending</option>
          <option value="fulfilled">Fulfilled</option>
          <option value="cancelled">Cancelled</option>
        </select>

        <select className="orders-sort" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="newest">Sort: Newest first</option>
          <option value="oldest">Sort: Oldest first</option>
          <option value="amount">Sort: Highest amount</option>
        </select>
      </div>

      <div className="orders-table-card">
        <h2>All Orders</h2>

        <div className="orders-table-scroll">
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Items</th>
                <th>Amount</th>
                <th>Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pageOrders.length === 0 && (
                <tr>
                  <td colSpan="7" className="orders-empty">
                    {orders.length === 0
                      ? "No orders yet. Click New Order to create one."
                      : "No orders match your search."}
                  </td>
                </tr>
              )}

              {pageOrders.map((o) => (
                <tr key={o.id}>
                  <td className="orders-id">#ORD-{String(o.id).padStart(5, "0")}</td>
                  <td>{o.customer_name}</td>
                  <td>{o.product_name} × {o.quantity}</td>
                  <td className="orders-amount">KES {Number(o.total_price).toLocaleString()}</td>
                  <td>{formatDate(o.date_of_sale)}</td>
                  <td>
                    <span className={"orders-status " + statusColors[o.status]}>{o.status}</span>
                  </td>
                  <td>
                    {o.status === "pending" ? (
                      <div className="orders-actions">
                        <button
                          className="orders-action orders-action-fulfil"
                          title="Fulfil order"
                          onClick={() => handleFulfil(o.id)}
                        >
                          ✓
                        </button>
                        <button
                          className="orders-action orders-action-cancel"
                          title="Cancel order"
                          onClick={() => handleCancel(o.id)}
                        >
                          ✕
                        </button>
                      </div>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="orders-footer">
          <span>
            Showing {showingFrom}–{showingTo} of {visible.length} orders
          </span>

          <div className="orders-pages">
            <button onClick={() => setPage(currentPage - 1)} disabled={currentPage === 1}>
              ‹
            </button>
            {pageNumbers.map((n) => (
              <button
                key={n}
                className={n === currentPage ? "active" : ""}
                onClick={() => setPage(n)}
              >
                {n}
              </button>
            ))}
            <button onClick={() => setPage(currentPage + 1)} disabled={currentPage === totalPages}>
              ›
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}