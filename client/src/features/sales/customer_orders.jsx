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

export default function CustomerOrders() {
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);

  const [customerId, setCustomerId] = useState("");
  const [productId, setProductId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

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

  return (
    <div>
      <h1>Customer Orders</h1>

      <form onSubmit={handleSubmit}>
        <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
          <option value="">Select a customer</option>
          {customers.map((c) => (
            <option key={c.id} value={c.id}>
              {c.customer_name}
            </option>
          ))}
        </select>

        <select value={productId} onChange={(e) => setProductId(e.target.value)}>
          <option value="">Select a product</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.product_name} - KES {p.price} ({p.quantity} in stock)
            </option>
          ))}
        </select>

        <input
          type="number"
          min="1"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />

        <button type="submit">Create order</button>
      </form>

      {message && <p>{message}</p>}

      {orders.length === 0 ? (
        <p>No orders yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Customer</th>
              <th>Product</th>
              <th>Qty</th>
              <th>Total (KES)</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>{o.id}</td>
                <td>{o.customer_name}</td>
                <td>{o.product_name}</td>
                <td>{o.quantity}</td>
                <td>{o.total_price}</td>
                <td>{o.status}</td>
                <td>
                  {o.status === "pending" && (
                    <>
                      <button onClick={() => handleFulfil(o.id)}>Fulfil</button>
                      <button onClick={() => handleCancel(o.id)}>Cancel</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}