import { api } from "./client";

export const getCustomers = () => api("/api/customers");

export const createCustomer = (data) =>
  api("/api/register_customer", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const deleteCustomer = (id) =>
  api(`/api/delete_customer/${id}`, {
    method: "DELETE",
  });

export const getProducts = () => api("/inventory");

export const getOrders = () => api("/api/customer_orders");

export const getCustomerHistory = () => api("/api/customer_history");

export const createOrder = (customerId, productId, quantity) =>
  api("/api/post_customer_orders", {
    method: "POST",
    body: JSON.stringify({
      customer_id: customerId,
      product_id: productId,
      quantity,
    }),
  });

export const cancelOrder = (id) =>
  api(`/api/cancel_customer_order/${id}`, {
    method: "PATCH",
  });

export const fulfilOrder = (id) =>
  api(`/api/fulfil_customer_order/${id}`, {
    method: "PATCH",
  });
