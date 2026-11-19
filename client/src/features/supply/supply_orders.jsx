import { useState, useEffect } from 'react'
import { api } from '../../api/client'

function SupplyOrders() {
    const [orders, setOrders] = useState([])
    const [suppliers, setSuppliers] = useState([])
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)
    const [submitting, setSubmitting] = useState(false)
    const [cancelling, setCancelling] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')

    //Fetch suppliers
    const fetchSuppliers = async () => {
        try {
            const data = await api('/suppliers')
            setSuppliers(data)
        } catch (error) {
            setError((previousError) =>
                previousError
                    ? `${previousError} | Suppliers: ${error.message}`
                    : `Suppliers: ${error.message}`
            )
        }
    }

    // Fetch products
    const fetchProducts = async () => {
        try {
            const data = await api('/inventory')
            setProducts(data)
        } catch (error) {
            setError((previousError) =>
                previousError
                    ? `${previousError} | Products: ${error.message}`
                    : `Products: ${error.message}`
            )
        }
    }

    // Fetch existing supply orders
    const fetchOrders = async () => {
        try {
            const data = await api('/supplyhistory')
            setOrders(data)
            return true 

        } catch (error) {
            setError((previousError) =>
                previousError
                    ? `${previousError} | Supply orders: ${error.message}`
                    : `Supply orders: ${error.message}`
            )
            return false

        } finally {
            setLoading(false)
        }
    }

    //Load suppliers and products on component mount
    useEffect(() => {
        fetchSuppliers()
        fetchProducts()
        fetchOrders()
    }, [])

    const [formData, setFormData] = useState({
        supplier_id: '',
        product_id: '',
        quantity: '',
        date_of_order: ''
    })

    //Handle form changes
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    //Submit order
    const handleSubmit = async (e) => {
        e.preventDefault()
        setSubmitting(true)
        setSuccess('')
        setError('')

        try {
            const token = localStorage.getItem('token')

            const response = await fetch(`${API_URL}/supply_orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    supplier_id: Number(formData.supplier_id),
                    product_id: Number(formData.product_id),
                    quantity: Number(formData.quantity),
                    date_of_order: formData.date_of_order
                })
            })

            const data = await response.json()

            if (!response.ok) {
                const errorMessage = typeof data.error === 'object' && data.error !== null
                    ? Object.values(data.error).map((message) => message.join(',')).join(',')
                    : data.error || data.message || 'Failed to create supply order.'

                throw new Error(errorMessage)
            }

            const refreshed = await fetchOrders()
            if (refreshed) {
                setSuccess('Supply order created successfully!')
                setError('')
            } else {
                setSuccess('Supply order created, but the order list could not be refreshed')
            }

            setFormData({
                supplier_id: '',
                product_id: '',
                quantity: '',
                date_of_order: ''
            })

        } catch (error) {
            setError(error.message)
        } finally {
            setSubmitting(false)
        }
    }

    //Cancel supply order
    const handleCancel = async (id) => {
        try {
            setCancelling(true)
            setSuccess('')

            const token = localStorage.getItem('token')

            const response = await fetch(`${API_URL}/cancel_order/${id}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ status: 'Cancelled' })
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.error || data.message || 'Failed to cancel order.')
            }

           setOrders((previousOrders) =>
                previousOrders.map((order) =>
                    order.id === id
                        ? {...order, status: 'Cancelled'}
                        : order
                )
            )

            setError('')
            setSuccess('Supply order cancelled successfully!')
        } catch (error) {
            setError(error.message)
        } finally {
            setCancelling(false)
        }
    }

    return (
        <div className="supply-orders-page">
            <h2>Supply Orders</h2>
            <p>View and manage your supply orders.</p>
            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}

            <form onSubmit={handleSubmit} className="order-form">
                <h3>Create Supply Order</h3>

                <select
                    name="supplier_id"
                    value={formData.supplier_id}
                    onChange={handleChange}
                    required
                >
                    <option value="">Select Supplier</option>
                    {suppliers.length === 0 && (
                        <option value="" disabled>No suppliers available</option>
                    )}
                    {suppliers.map((supplier) => (
                        <option key={supplier.id} value={supplier.id}>
                            {supplier.name}
                        </option>
                    ))}
                </select>

                <select
                    name="product_id"
                    value={formData.product_id}
                    onChange={handleChange}
                    required
                >
                    <option value="">Select Product</option>
                    {products.length === 0 && (
                        <option value="" disabled>No products available</option>
                    )}
                    {products.map((product) => (
                        <option key={product.id} value={product.id}>
                            {product.product_name}
                        </option>
                    ))}
                </select>

                <input
                    type="number"
                    name="quantity"
                    placeholder="Quantity"
                    min="1"
                    value={formData.quantity}
                    onChange={handleChange}
                    required
                />

                <input
                    type="date"
                    name="date_of_order"
                    value={formData.date_of_order}
                    onChange={handleChange}
                    required
                />

                <button 
                type="submit" 
                disabled={submitting || suppliers.length === 0 || products.length === 0}
                >
                {submitting ? 'Creating...' : 'Create Order'}
                </button>
                
            </form>

            <div className="orders-list">
                <h3>All Supply Orders</h3>

                {loading ? (
                    <p>Loading supply orders...</p>
                ) : orders.length === 0 ? (
                    <p>No supply orders found.</p>
                ) : ( 
                    <table>
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Supplier</th>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Order Date</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            {orders.map((order) => (
                                <tr key={order.id}>
                                    <td>{order.id}</td>
                                    <td>{order.supplier?.name}</td>
                                    <td>{products.find((product) => product.id === order.product_id)?.product_name || order.product_id}</td>
                                    <td>{order.quantity}</td>
                                    <td>{order.date_of_order}</td>
                                    <td>{order.status}</td>
                                    <td>
                                        {order.status === 'Pending' && (
                                                <button
                                                    onClick={() => handleCancel(order.id)} disabled={cancelling}>
                                                    {cancelling ? 'Cancelling...' : 'Cancel'}
                                                </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}

export default SupplyOrders

 
    