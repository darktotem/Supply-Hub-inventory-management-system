import { useCallback, useEffect, useState } from 'react'
import './warehouse.css'
import { warehouseRequest } from './warehouseApi.js'

function formatDate(value) {
  if (!value) return '—'
  return new Date(`${value}T00:00:00`).toLocaleDateString()
}

function statusClass(status) {
  return `status-badge--${(status || 'pending').toLowerCase()}`
}

function Deliveries() {
  const [deliveries, setDeliveries] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeDelivery, setActiveDelivery] = useState(null)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const loadDeliveries = useCallback(async () => {
    setError('')
    setIsLoading(true)
    try {
      const data = await warehouseRequest('/warehouse/deliveries')
      setDeliveries(data)
    } catch (loadError) {
      setError(loadError.message)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    let isActive = true
    warehouseRequest('/warehouse/deliveries')
      .then((data) => {
        if (isActive) setDeliveries(data)
      })
      .catch((loadError) => {
        if (isActive) setError(loadError.message)
      })
      .finally(() => {
        if (isActive) setIsLoading(false)
      })

    return () => {
      isActive = false
    }
  }, [])

  async function markDelivered(deliveryId) {
    setActiveDelivery(deliveryId)
    setError('')
    setNotice('')
    try {
      await warehouseRequest(`/warehouse/deliveries/${deliveryId}/deliver`, {
        method: 'PATCH',
      })
      setNotice('Delivery received and inventory updated.')
      await loadDeliveries()
    } catch (actionError) {
      setError(actionError.message)
    } finally {
      setActiveDelivery(null)
    }
  }

  return (
    <main className="page-container deliveries-page">
      <header className="page-header">
        <div>
          <h1>Deliveries</h1>
          <p>Review incoming supply orders and receive deliveries into inventory.</p>
        </div>
        <button className="secondary-btn" type="button" onClick={loadDeliveries} disabled={isLoading}>
          Refresh
        </button>
      </header>

      {error && <div className="warehouse-alert warehouse-alert--error" role="alert">{error}</div>}
      {notice && <div className="warehouse-alert warehouse-alert--success" role="status">{notice}</div>}

      <section className="section-card" aria-labelledby="deliveries-title">
        <h2 id="deliveries-title">Supply orders</h2>
        {isLoading ? (
          <p className="warehouse-loading" role="status">Loading deliveries...</p>
        ) : deliveries.length === 0 ? (
          <p className="warehouse-empty">No deliveries found.</p>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th scope="col">Order</th>
                  <th scope="col">Product</th>
                  <th scope="col">Supplier</th>
                  <th scope="col">Quantity</th>
                  <th scope="col">Order date</th>
                  <th scope="col">Delivery date</th>
                  <th scope="col">Status</th>
                  <th scope="col">Action</th>
                </tr>
              </thead>
              <tbody>
                {deliveries.map((delivery) => (
                  <tr key={delivery.id}>
                    <td>#{delivery.id}</td>
                    <td>Product #{delivery.product_id}</td>
                    <td>{delivery.supplier?.name || `Supplier #${delivery.supplier_id}`}</td>
                    <td>{delivery.quantity}</td>
                    <td>{formatDate(delivery.date_of_order)}</td>
                    <td>{formatDate(delivery.date_of_delivery)}</td>
                    <td>
                      <span className={`status-badge ${statusClass(delivery.status)}`}>
                        {delivery.status || 'Pending'}
                      </span>
                    </td>
                    <td>
                      {delivery.status === 'Pending' ? (
                        <button
                          className="primary-btn"
                          type="button"
                          onClick={() => markDelivered(delivery.id)}
                          disabled={activeDelivery === delivery.id}
                        >
                          {activeDelivery === delivery.id ? 'Receiving...' : 'Mark delivered'}
                        </button>
                      ) : (
                        <span className="warehouse-muted">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  )
}

export default Deliveries