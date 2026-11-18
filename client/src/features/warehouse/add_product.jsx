import { useState } from 'react'
import './warehouse.css'
import { warehouseRequest } from './warehouseApi.js'

const initialProduct = {
  product_name: '',
  category: '',
  quantity: '',
  threshold: '',
  price: '',
}

function AddProduct() {
  const [product, setProduct] = useState(initialProduct)
  const [message, setMessage] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleChange(event) {
    const { name, value } = event.target
    setProduct((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setMessage(null)
    setIsSubmitting(true)

    try {
      await warehouseRequest('/warehouse/products', {
        method: 'POST',
        body: {
          ...product,
          quantity: Number(product.quantity),
          threshold: Number(product.threshold),
          price: Number(product.price),
        },
      })
      setProduct(initialProduct)
      setMessage({ type: 'success', text: 'Product added to inventory.' })
    } catch (error) {
      setMessage({ type: 'error', text: error.message })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="page-container add-product-page">
      <header className="page-header">
        <div>
          <h1>Add Product</h1>
          <p>Register a product and set its current stock and reorder threshold.</p>
        </div>
      </header>

      <section className="form-container" aria-labelledby="product-form-title">
        <h2 id="product-form-title">Product details</h2>
        {message && (
          <div className={`warehouse-alert warehouse-alert--${message.type}`} role="status">
            {message.text}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="product_name">Product name</label>
              <input
                className="input-field"
                id="product_name"
                name="product_name"
                type="text"
                maxLength={150}
                value={product.product_name}
                onChange={handleChange}
                placeholder="e.g. Whole grain rice"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="category">Category</label>
              <input
                className="input-field"
                id="category"
                name="category"
                type="text"
                maxLength={100}
                value={product.category}
                onChange={handleChange}
                placeholder="e.g. Grains"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="quantity">Quantity in stock</label>
              <input
                className="input-field"
                id="quantity"
                name="quantity"
                type="number"
                min="0"
                step="1"
                value={product.quantity}
                onChange={handleChange}
                placeholder="0"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="threshold">Low-stock threshold</label>
              <input
                className="input-field"
                id="threshold"
                name="threshold"
                type="number"
                min="0"
                step="1"
                value={product.threshold}
                onChange={handleChange}
                placeholder="10"
                required
              />
            </div>
            <div className="form-group form-group--full">
              <label htmlFor="price">Unit price</label>
              <input
                className="input-field"
                id="price"
                name="price"
                type="number"
                min="0"
                step="0.01"
                value={product.price}
                onChange={handleChange}
                placeholder="0.00"
                required
              />
            </div>
            <div className="form-group form-group--full form-actions">
              <button className="primary-btn" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Saving product...' : 'Add product'}
              </button>
            </div>
          </div>
        </form>
      </section>
    </main>
  )
}

export default AddProduct