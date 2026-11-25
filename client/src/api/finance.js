import { api } from "./client";


export const getInvoices = async () => {
  return api("/invoices/");
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

return api("/invoices/", {
  method: "POST",
  body: JSON.stringify(body),
}); 
};


export const getPayments = async (invoiceId) => {
  return api(`/invoices/${invoiceId}/payments`);
};


export const addPayment = async (invoiceId, { amount, method = "cash", reference }) => {
const body = { amount: String(amount), method };
if (reference) body.reference = reference;

return api(`/invoices/${invoiceId}/payments`, {
  method: "POST",
  body: JSON.stringify(body),
}); 
};
