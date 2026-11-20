// @ts-nocheck
const API_BASE = (import.meta.env.VITE_API_URL || "http://127.0.0.1:5000").replace(/\/$/, "");

export function getToken() {
  return localStorage.getItem("supply_hub_token");
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.error
      || (data.errors && Object.values(data.errors).flat().join(" "))
      || "The request could not be completed";
    throw new Error(message);
  }
  return data;
}
