import { useEffect, useMemo, useState } from "react";
import {
  getWarehouseDeliveries,
  receiveWarehouseDelivery,
} from "../../api/warehouse";
import "./warehouse.css";

function Deliveries() {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [receivingId, setReceivingId] = useState(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadDeliveries() {
      try {
        const data = await getWarehouseDeliveries();
        if (!cancelled) setDeliveries(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Could not load deliveries.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadDeliveries();
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredDeliveries = useMemo(
    () =>
      deliveries.filter((delivery) =>
        statusFilter === "all" ||
        String(delivery.status || "").toLowerCase() === statusFilter
      ),
    [deliveries, statusFilter]
  );

  const pendingCount = deliveries.filter(
    (delivery) => delivery.status === "Pending"
  ).length;

  async function handleReceive(delivery) {
    setError("");
    setSuccess("");
    setReceivingId(delivery.id);

    try {
      const result = await receiveWarehouseDelivery(delivery.id);
      const updatedOrder = result.order;
      setDeliveries((previous) =>
        previous.map((item) =>
          item.id === delivery.id ? { ...item, ...updatedOrder } : item
        )
      );
      setSuccess(`Delivery #${delivery.id} received and inventory updated.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not receive this delivery.");
    } finally {
      setReceivingId(null);
    }
  }

  return (
    <section className="warehouse-page" aria-labelledby="warehouse-deliveries-title">
      <header className="warehouse-heading">
        <div>
          <p className="warehouse-eyebrow">Warehouse / Inbound stock</p>
          <h1 id="warehouse-deliveries-title">Deliveries</h1>
          <p>Track incoming supply orders and receive stock into inventory.</p>
        </div>
        <label className="warehouse-filter">
          <span>Status</span>
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="all">All deliveries</option>
            <option value="pending">Pending</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </label>
      </header>

      <div className="warehouse-stats">
        <article className="warehouse-stat">
          <span>Total deliveries</span>
          <strong>{deliveries.length}</strong>
          <small>All supply orders</small>
        </article>
        <article className="warehouse-stat warehouse-stat-warning">
          <span>Awaiting receipt</span>
          <strong>{pendingCount}</strong>
          <small>Pending warehouse deliveries</small>
        </article>
        <article className="warehouse-stat">
          <span>Received</span>
          <strong>{deliveries.filter((item) => item.status === "Delivered").length}</strong>
          <small>Stock added to inventory</small>
        </article>
      </div>

      <section className="warehouse-panel">
        <div className="warehouse-panel-heading">
          <div>
            <h2>Delivery register</h2>
            <p>Receiving a delivery updates the product stock count.</p>
          </div>
        </div>

        {error && <div className="warehouse-alert warehouse-alert-error" role="alert">{error}</div>}
        {success && <div className="warehouse-alert warehouse-alert-success" role="status">{success}</div>}

        {loading ? (
          <p className="warehouse-empty-state">Loading deliveries…</p>
        ) : filteredDeliveries.length === 0 ? (
          <p className="warehouse-empty-state">No deliveries found for this filter.</p>
        ) : (
          <div className="warehouse-table-scroll">
            <table className="warehouse-table">
              <thead>
                <tr>
                  <th>Delivery</th>
                  <th>Supplier</th>
                  <th>Product ID</th>
                  <th>Quantity</th>
                  <th>Order date</th>
                  <th>Received date</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredDeliveries.map((delivery) => {
                  const status = String(delivery.status || "Unknown").toLowerCase();
                  return (
                    <tr key={delivery.id}>
                      <td><strong>#{delivery.id}</strong></td>
                      <td>{delivery.supplier?.name || "—"}</td>
                      <td>{delivery.product_id}</td>
                      <td>{delivery.quantity}</td>
                      <td>{delivery.date_of_order || "—"}</td>
                      <td>{delivery.date_of_delivery || "—"}</td>
                      <td>
                        <span className={`warehouse-badge warehouse-badge-${status}`}>
                          {delivery.status || "Unknown"}
                        </span>
                      </td>
                      <td>
                        {delivery.status === "Pending" ? (
                          <button
                            className="warehouse-small-button"
                            type="button"
                            onClick={() => handleReceive(delivery)}
                            disabled={receivingId === delivery.id}
                          >
                            {receivingId === delivery.id ? "Receiving…" : "Receive"}
                          </button>
                        ) : <span className="warehouse-muted">—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  );
}

export default Deliveries;