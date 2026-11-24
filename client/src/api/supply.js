import { api } from "./client";

//Suppliers
export function getSuppliers() {
    return api("/suppliers");
}

export function registerSupplier(supplierData) {
    return api("/register_supplier", {
        method: "POST",
        body: JSON.stringify(supplierData),
    });
}

export function deleteSupplier(supplierId) {
    return api(`/delete_suppliers/${supplierId}`, {
        method: "DELETE",
    });
}

//Inventory
export function getInventory() {
    return api("/inventory");
}

//Supply history and orders
export function getSupplyHistory() {
    return api("/supplyhistory");
}

export function createSupplyOrder(orderData) {
    return api("/supply_orders", {
        method: "POST",
        body: JSON.stringify(orderData),
    });
}

export function cancelSupplyOrder(orderId) {
    return api(`/cancel_order/${orderId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: "Cancelled" }),
    });
}

export function deliverSupplyOrder(orderId, deliveryDate) {
  return api(`/deliver_order/${orderId}`, {
    method: "PATCH",
    body: JSON.stringify({ date_of_delivery: deliveryDate }),
  });
}