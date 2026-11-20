import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:5000",
  headers: { "Content-Type": "application/json" },
});
// Note the trailing slash: your GET route is "/invoices/" and has no
// strict_slashes=False, so "/invoices" triggers a redirect that can
// trip up CORS.
export const getInvoices = async () => {
  const { data } = await api.get("/invoices/");
  return data;
};

// Money fields are sent as strings ("100.00") to avoid float rounding,
// matching how the backend's money() helper parses them.
export const createInvoice = async ({ customer_id, product_id, sale_id, unit_price, quantity, total }) => {
  const body = {
    customer_id,
    product_id,
    sale_id,
    unit_price: String(unit_price),
    quantity,
  };
  if (total !== undefined && total !== "") body.total = String(total);

  const { data } = await api.post("/invoices/", body);
  return data; // { message, invoice }
};

export const getPayments = async (invoiceId) => {
  const { data } = await api.get(`/invoices/${invoiceId}/payments`);
  return data;
};

// method: "cash" | "mpesa" | "bank" | "card"
export const addPayment = async (invoiceId, { amount, method = "cash", reference }) => {
  const body = { amount: String(amount), method };
  if (reference) body.reference = reference;

  const { data } = await api.post(`/invoices/${invoiceId}/payments`, body);
  return data; // { message, payment, invoice }
};