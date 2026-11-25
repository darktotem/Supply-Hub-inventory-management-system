// @ts-nocheck
const API_BASE = (import.meta.env.VITE_API_URL || "http://127.0.0.1:5000")
  .trim()
  .replace(/\/+$/, "");

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

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  } catch {
    throw new Error("Cannot reach the server");
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    let message = "The request could not be completed";

    if (typeof data.error === "string") {
      message = data.error;
    } else if (data.errors) {
      message = Object.entries(data.errors)
        .map(([field, messages]) => {
          const text = Array.isArray(messages) ? messages.join(" ") : String(messages);
          const fieldLabel = field.replace(/_/g, " ").replace(/^./, (char) => char.toUpperCase());
          return `${fieldLabel}: ${text}`;
        })
        .join(" ");
    } else if (data.error && typeof data.error === "object") {
      message = Object.entries(data.error)
        .map(([field, messages]) => {
          const text = Array.isArray(messages) ? messages.join(" ") : String(messages);
          return `${field.replace(/_/g, " ")}: ${text}`;
        })
        .join(" ");
    }

    throw new Error(message);
  }
  return data;
}
