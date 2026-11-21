import { api } from "./client";

export const getWarehouseProducts = () => api("/warehouse/products");

export const createWarehouseProduct = (product) =>
  api("/warehouse/products", {
    method: "POST",
    body: JSON.stringify(product),
  });

export const getWarehouseDeliveries = () => api("/warehouse/deliveries");

export const receiveWarehouseDelivery = (id) =>
  api(`/warehouse/deliveries/${id}/deliver`, {
    method: "PATCH",
  });

export const getWarehouseReport = () => api("/warehouse/reports");

export const saveWarehouseReport = () =>
  api("/warehouse/reports", {
    method: "POST",
  });

export const getWarehouseReportHistory = () =>
  api("/warehouse/reports/history");