// @ts-nocheck
import { useEffect, useState } from "react";
import { getCustomers, createCustomer, deleteCustomer } from "../../api/sales";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [customerName, setCustomerName] = useState("");
  const [contact, setContact] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  // Load customers when the page opens
  useEffect(() => {
    loadCustomers();
  }, []);

  async function loadCustomers() {
    try {
      const data = await getCustomers();
      setCustomers(data);
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
      loadCustomers();
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteCustomer(id);
      setMessage("");
      loadCustomers();
    } catch (err) {
      setMessage(err.message);
    }
  }

  if (loading) {
    return <p>Loading customers...</p>;
  }

  return (
    <div>
      <h1>Customers</h1>

      <form onSubmit={handleSubmit}>
        <input
          placeholder="Name"
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
        />
        <input
          placeholder="Phone"
          value={contact}
          onChange={(e) => setContact(e.target.value)}
        />
        <button type="submit">Add customer</button>
      </form>

      {message && <p>{message}</p>}

      {customers.length === 0 ? (
        <p>No customers yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Phone</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((c) => (
              <tr key={c.id}>
                <td>{c.customer_name}</td>
                <td>{c.contact}</td>
                <td>
                  <button onClick={() => handleDelete(c.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}