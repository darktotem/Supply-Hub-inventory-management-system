// @ts-nocheck

import { api } from "./client";

function request(path, options) {
  return api(path, options);
}


// ----- Customers -----

export function getCustomers() {
  return request("/api/customers");
}

export function createCustomer(customer) {
  return request("/api/register_customer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(customer),
  });
}

export function deleteCustomer(id) {
  return request("/api/delete_customer/" + id, { method: "DELETE" });
}


// ----- Products (read only) -----

export function getProducts() {
  return request("/inventory");
}


// ----- Customer orders -----

export function getOrders() {
  return request("/api/customer_orders");
}

export function createOrder(customerId, productId, quantity) {
  return request("/api/post_customer_orders", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      customer_id: customerId,
      product_id: productId,
      quantity: quantity,
    }),
  });
}

export function cancelOrder(id) {
  return request("/api/cancel_customer_order/" + id, { method: "PATCH" });
}

export function fulfilOrder(id) {
  return request("/api/fulfil_customer_order/" + id, { method: "PATCH" });
}
