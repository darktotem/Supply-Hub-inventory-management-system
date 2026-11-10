// Fake data. It resets when you refresh the page.
let customers = [
  { id: 1, name: "Amina Wanjiru", email: "amina@example.com", phone: "0712345678" },
  { id: 2, name: "Brian Otieno", email: "brian@example.com", phone: "0723456789" },
];

// TODO: replace with the team's inventory API
let products = [
  { id: 1, name: "Rice 2kg", price: 350, stock: 40 },
  { id: 2, name: "Cooking Oil 1L", price: 280, stock: 25 },
  { id: 3, name: "Sugar 1kg", price: 190, stock: 5 },
];

let orders = [];
let nextCustomerId = 3;
let nextOrderId = 1;

// ----- Customers -----

export async function getCustomers() {
  return [...customers];
}

export async function createCustomer(data) {
  const customer = { id: nextCustomerId, ...data };
  nextCustomerId = nextCustomerId + 1;
  customers.push(customer);
  return customer;
}

export async function deleteCustomer(id) {
  customers = customers.filter((c) => c.id !== id);
}

// ----- Products -----

export async function getProducts() {
  return [...products];
}

// ----- Orders -----

export async function getOrders() {
  return [...orders];
}

export async function createOrder(customerId, productId, quantity) {
  const product = products.find((p) => p.id === productId);

  if (quantity > product.stock) {
    throw new Error("Not enough stock. Only " + product.stock + " left.");
  }

  const order = {
    id: nextOrderId,
    customerId: customerId,
    productName: product.name,
    quantity: quantity,
    total: product.price * quantity,
    status: "pending",
  };
  nextOrderId = nextOrderId + 1;
  orders.push(order);
  return order;
}

export async function cancelOrder(id) {
  const order = orders.find((o) => o.id === id);
  order.status = "cancelled";
}

export async function fulfilOrder(id) {
  const order = orders.find((o) => o.id === id);
  const product = products.find((p) => p.name === order.productName);

  if (order.quantity > product.stock) {
    throw new Error("Not enough stock to fulfil this order.");
  }

  product.stock = product.stock - order.quantity;
  order.status = "fulfilled";
}