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

  // Load everything when the page opens
  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setCustomers(await getCustomers());
    setProducts(await getProducts());
    setOrders(await getOrders());
  }

  // Turn a customer id into a name for the table
  function getCustomerName(id) {
    const customer = customers.find((c) => c.id === id);
    return customer ? customer.name : "Unknown";
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
    await cancelOrder(id);
    loadData();
  }

  async function handleFulfil(id) {
    try {
      await fulfilOrder(id);
      loadData();
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <div>
      <h1>Customer Orders</h1>

      <form onSubmit={handleSubmit}>
        <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
          <option value="">Select a customer</option>
          {customers.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>

        <select value={productId} onChange={(e) => setProductId(e.target.value)}>
          <option value="">Select a product</option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} - KES {p.price} ({p.stock} in stock)
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
                <td>{getCustomerName(o.customerId)}</td>
                <td>{o.productName}</td>
                <td>{o.quantity}</td>
                <td>{o.total}</td>
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