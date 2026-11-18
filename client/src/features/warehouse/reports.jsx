import { useCallback, useEffect, useState } from 'react'
import './warehouse.css'
import { warehouseRequest } from './warehouseApi.js'

/**
 * @typedef {{
 *   id: number,
 *   product_name: string,
 *   category: string,
 *   quantity: number,
 *   threshold: number,
 *   price: number
 * }} InventoryItem
 */

/**
 * @typedef {{
 *   id: number | null,
 *   report_type: string,
 *   generated_at: string | null,
 *   total_products: number,
 *   total_quantity: number,
 *   low_stock_count: number,
 *   low_stock_items: InventoryItem[],
 *   inventory: InventoryItem[]
 * }} InventoryReport
 */

/** @param {unknown} error */
function errorMessage(error) {
  return error instanceof Error ? error.message : 'An unexpected error occurred.'
}

/** @param {string | null} value */
function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

/** @param {number | null | undefined} value */
function formatPrice(value) {
  return (value ?? 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function Reports() {
  const [report, setReport] = useState(/** @type {InventoryReport | null} */ (null))
  const [history, setHistory] = useState(/** @type {InventoryReport[]} */ ([]))
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const loadReports = useCallback(async () => {
    setError('')
    setIsLoading(true)
    try {
      const [currentReport, reportHistory] = await Promise.all([
        warehouseRequest('/warehouse/reports'),
        warehouseRequest('/warehouse/reports/history'),
      ])
      setReport(currentReport)
      setHistory(reportHistory)
    } catch (loadError) {
      setError(errorMessage(loadError))
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    let isActive = true
    Promise.all([
      warehouseRequest('/warehouse/reports'),
      warehouseRequest('/warehouse/reports/history'),
    ])
      .then(([currentReport, reportHistory]) => {
        if (isActive) {
          setReport(currentReport)
          setHistory(reportHistory)
        }
      })
      .catch((loadError) => {
        if (isActive) setError(errorMessage(loadError))
      })
      .finally(() => {
        if (isActive) setIsLoading(false)
      })

    return () => {
      isActive = false
    }
  }, [])

  async function saveReport() {
    setError('')
    setNotice('')
    setIsSaving(true)
    try {
      const savedReport = await warehouseRequest('/warehouse/reports', { method: 'POST' })
      setHistory((current) => [savedReport, ...current])
      setNotice('Inventory report saved.')
    } catch (saveError) {
      setError(errorMessage(saveError))
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <main className="page-container reports-page">
      <header className="page-header">
        <div>
          <h1>Inventory Reports</h1>
          <p>Monitor stock levels and review saved inventory snapshots.</p>
        </div>
        <div className="page-toolbar">
          <button className="secondary-btn" type="button" onClick={loadReports} disabled={isLoading}>
            Refresh
          </button>
          <button className="primary-btn" type="button" onClick={saveReport} disabled={isSaving || isLoading}>
            {isSaving ? 'Saving...' : 'Save report'}
          </button>
        </div>
      </header>

      {error && <div className="warehouse-alert warehouse-alert--error" role="alert">{error}</div>}
      {notice && <div className="warehouse-alert warehouse-alert--success" role="status">{notice}</div>}

      {isLoading ? (
        <section className="section-card">
          <p className="warehouse-loading" role="status">Loading inventory report...</p>
        </section>
      ) : report ? (
        <>
          <section className="stats-grid" aria-label="Inventory summary">
            <article className="stats-card">
              <span className="stats-card__label">Total products</span>
              <strong className="stats-card__value">{report.total_products}</strong>
            </article>
            <article className="stats-card">
              <span className="stats-card__label">Units in stock</span>
              <strong className="stats-card__value">{report.total_quantity}</strong>
            </article>
            <article className="stats-card">
              <span className="stats-card__label">Low-stock products</span>
              <strong className="stats-card__value">{report.low_stock_count}</strong>
            </article>
            <article className="stats-card">
              <span className="stats-card__label">Report generated</span>
              <strong className="stats-card__date">{formatDate(report.generated_at)}</strong>
            </article>
          </section>

          <section className="section-card" aria-labelledby="low-stock-title">
            <h2 id="low-stock-title">Low-stock items</h2>
            {report.low_stock_items?.length ? (
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th scope="col">Product</th>
                      <th scope="col">Category</th>
                      <th scope="col">Quantity</th>
                      <th scope="col">Threshold</th>
                      <th scope="col">Unit price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.low_stock_items.map((item) => (
                      <tr key={item.id}>
                        <td>{item.product_name}</td>
                        <td>{item.category}</td>
                        <td>{item.quantity}</td>
                        <td>{item.threshold}</td>
                        <td>{formatPrice(item.price)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="warehouse-empty">All products are above their stock thresholds.</p>
            )}
          </section>

          <section className="section-card" aria-labelledby="inventory-title">
            <h2 id="inventory-title">Inventory overview</h2>
            {report.inventory?.length ? (
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th scope="col">Product</th>
                      <th scope="col">Category</th>
                      <th scope="col">Quantity</th>
                      <th scope="col">Unit price</th>
                      <th scope="col">Stock status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.inventory.map((item) => {
                      const isLowStock = item.quantity <= item.threshold
                      return (
                        <tr key={item.id}>
                          <td>{item.product_name}</td>
                          <td>{item.category}</td>
                          <td>{item.quantity}</td>
                          <td>{formatPrice(item.price)}</td>
                          <td>
                            <span className={`status-badge status-badge--${isLowStock ? 'pending' : 'delivered'}`}>
                              {isLowStock ? 'Low stock' : 'In stock'}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="warehouse-empty">No inventory items to report.</p>
            )}
          </section>
        </>
      ) : null}

      <section className="section-card" aria-labelledby="history-title">
        <h2 id="history-title">Saved report history</h2>
        {history.length ? (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th scope="col">Report</th>
                  <th scope="col">Generated</th>
                  <th scope="col">Products</th>
                  <th scope="col">Units</th>
                  <th scope="col">Low-stock items</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.id}>
                    <td>#{item.id}</td>
                    <td>{formatDate(item.generated_at)}</td>
                    <td>{item.total_products}</td>
                    <td>{item.total_quantity}</td>
                    <td>{item.low_stock_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="warehouse-empty">No saved reports yet.</p>
        )}
      </section>
    </main>
  )
}

export default Reports