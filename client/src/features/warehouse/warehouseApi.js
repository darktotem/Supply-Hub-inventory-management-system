const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(
  /\/$/,
  '',
)

/**
 * @typedef {Omit<RequestInit, 'body'> & { body?: unknown }} WarehouseRequestOptions
 */

/**
 * @param {string} path
 * @param {WarehouseRequestOptions} [options={}]
 */
export async function warehouseRequest(path, options = {}) {
  const { body, ...requestOptions } = options
  const headers = new Headers(requestOptions.headers)
  if (body !== undefined) headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await response.json()

  if (!response.ok) {
    const details = data.error || data.message || data.errors
    throw new Error(
      typeof details === 'string'
        ? details
        : details
          ? JSON.stringify(details)
          : `Warehouse request failed (${response.status})`,
    )
  }

  return data
}
