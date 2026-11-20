import axios from "axios";

const api = axios.create({
baseURL: import.meta.env.VITE_API_URL,
headers: { "Content-Type": "application/json" },
});


export const getInvoices = async () => {
const { data } = await api.get("/invoices/");
return data;
};


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
return data; 
};

export const getPayments = async (invoiceId) => {
const { data } = await api.get(`/invoices/${invoiceId}/payments`);
return data;
};

export const addPayment = async (invoiceId, { amount, method = "cash", reference }) => {
const body = { amount: String(amount), method };
if (reference) body.reference = reference;

const { data } = await api.post(`/invoices/${invoiceId}/payments`, body);
return data; 
};
