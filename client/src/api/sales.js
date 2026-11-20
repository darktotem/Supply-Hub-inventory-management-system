// @ts-nocheck
const BASE_URL = "http://localhost:5000";


// Sends a request to the backend and returns the JSON answer.
// If the backend says something is wrong, it throws an Error with the message.
async function request(path, options) {
  let response;

  try {
    response = await fetch(BASE_URL + path, options);
  } catch (err) {
    throw new Error("Cannot reach the server. Is it running?", { cause: err });
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(getErrorMessage(data));
  }

  return data;
}


// The backend sends errors in two shapes: {"error": "text"} or {"errors": {"field": ["text"]}}
function getErrorMessage(data) {
  if (data.error) {
    return data.error;
  }
  if (data.errors) {
    return Object.values(data.errors).flat().join(" ");
  }
  return "Something went wrong.";
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