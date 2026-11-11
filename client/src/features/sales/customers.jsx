import { useEffect, useState } from "react";
import { getCustomers, createCustomer, deleteCustomer } from "../../api/sales";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [message, setMessage] = useState("");

  // Load customers when the page opens
  useEffect(() => {
    loadCustomers();
  }, []);

  async function loadCustomers() {
    const data = await getCustomers();
    setCustomers(data);
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (name === "" || email === "" || phone === "") {
      setMessage("Please fill in all fields.");
      return;
    }

    await createCustomer({ name, email, phone });
    setName("");
    setEmail("");
    setPhone("");
    setMessage("");
    loadCustomers();
  }

  async function handleDelete(id) {
    await deleteCustomer(id);
    loadCustomers();
  }

  return (
    <div>
      <h1>Customers</h1>

      <form onSubmit={handleSubmit}>
        <input
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          placeholder="Phone"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
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
              <th>Email</th>
              <th>Phone</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.email}</td>
                <td>{c.phone}</td>
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