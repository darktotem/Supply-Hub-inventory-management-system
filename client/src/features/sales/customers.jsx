// @ts-nocheck
import { useEffect, useState } from "react";
import { getCustomers, createCustomer, deleteCustomer, getOrders } from "../../api/sales";
import "./sales.css";

const PAGE_SIZE = 8;

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  // New customer form
  const [showForm, setShowForm] = useState(false);
  const [customerName, setCustomerName] = useState("");
  const [contact, setContact] = useState("");

  // Search and pages
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  // Load everything when the page opens
  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setCustomers(await getCustomers());
      setOrders(await getOrders());
    } catch (err) {
      setMessage(err.message);
    }
    setLoading(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (customerName === "" || contact === "") {
      setMessage("Please fill in all fields.");
      return;
    }

    try {
      await createCustomer({ customer_name: customerName, contact: contact });
      setCustomerName("");
      setContact("");
      setMessage("");
      setShowForm(false);
      loadData();
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this customer?")) {
      return;
    }

    try {
      await deleteCustomer(id);
      setMessage("");
      loadData();
    } catch (err) {
      setMessage(err.message);
    }
  }

  if (loading) {
    return <p>Loading customers...</p>;
  }

  // How many orders one customer has placed
  function countOrders(customerId) {
    return orders.filter((o) => o.customer_id === customerId).length;
  }

  // ----- Numbers for the four cards -----
  const total = customers.length;
  const withOrders = customers.filter((c) => countOrders(c.id) > 0).length;
  const withoutOrders = total - withOrders;

  function percent(count) {
    if (total === 0) return 0;
    return Math.round((count / total) * 100);
  }

  const stats = [
    { label: "Total Customers", count: total, icon: "👥", color: "orders-purple", note: "All customers" },
    { label: "With Orders", count: withOrders, icon: "🛒", color: "orders-green", note: percent(withOrders) + "% of customers" },
    { label: "No Orders Yet", count: withoutOrders, icon: "🕒", color: "orders-orange", note: percent(withoutOrders) + "% of customers" },
    { label: "Orders Placed", count: orders.length, icon: "📦", color: "orders-purple", note: "All time" },
  ];

  // ----- Search -----
  const visible = customers.filter((c) => {
    const text = (c.customer_name + " " + c.contact).toLowerCase();
    return text.includes(search.toLowerCase());
  });

  // ----- Pages -----
  const totalPages = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const pageCustomers = visible.slice(startIndex, startIndex + PAGE_SIZE);
  const showingFrom = visible.length === 0 ? 0 : startIndex + 1;
  const showingTo = startIndex + pageCustomers.length;
  const pageNumbers = Array.from({ length: totalPages }, (_, i) => i + 1);

  return (
    <div className="orders-page">
      <div className="orders-header">
        <div>
          <h1>Customers</h1>
          <p className="orders-subtitle">Manage the customers you sell to</p>
        </div>
        <div className="orders-header-buttons">
          <button className="orders-btn orders-btn-primary" onClick={() => setShowForm(!showForm)}>
            + New Customer
          </button>
        </div>
      </div>

      {message && <p className="orders-message">{message}</p>}

      {showForm && (
        <form className="orders-form" onSubmit={handleSubmit}>
          <label>
            Name
            <input
              placeholder="e.g. Amina Wanjiru"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
            />
          </label>

          <label>
            Phone
            <input
              placeholder="e.g. 0712345678"
              value={contact}
              onChange={(e) => setContact(e.target.value)}
            />
          </label>

          <button className="orders-btn orders-btn-primary" type="submit">
            Add customer
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
          placeholder="Search by name or phone..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
      </div>

      <div className="orders-table-card">
        <h2>All Customers</h2>

        <div className="orders-table-scroll">
          <table>
            <thead>
              <tr>
                <th>Customer ID</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Orders</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pageCustomers.length === 0 && (
                <tr>
                  <td colSpan="5" className="orders-empty">
                    {customers.length === 0
                      ? "No customers yet. Click New Customer to add one."
                      : "No customers match your search."}
                  </td>
                </tr>
              )}

              {pageCustomers.map((c) => (
                <tr key={c.id}>
                  <td className="orders-id">#CUS-{String(c.id).padStart(5, "0")}</td>
                  <td>{c.customer_name}</td>
                  <td>{c.contact}</td>
                  <td>{countOrders(c.id)}</td>
                  <td>
                    {countOrders(c.id) === 0 ? (
                      <div className="orders-actions">
                        <button
                          className="orders-action orders-action-cancel"
                          title="Delete customer"
                          onClick={() => handleDelete(c.id)}
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
            Showing {showingFrom}–{showingTo} of {visible.length} customers
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