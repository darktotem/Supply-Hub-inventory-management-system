import { api } from "./client";

export const getInventory = () => api("/inventory");

export const createInventory = (data) =>
  api("/inventory", {
    method: "POST",
    body: JSON.stringify(data),
  });

export const updateInventory = (id, data) =>
  api(`/inventory/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });

export const deleteInventory = (id) =>
  api(`/inventory/${id}`, {
    method: "DELETE",
  });