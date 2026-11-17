import { useState, useEffect } from 'react'

const API_URL = 'http://127.0.0.1:5000'

function SupplyOrders() {
    const [orders, setOrders] = useState([])
    const [suppliers, setSuppliers] = useState([])
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    //Fetch suppliers
    const fetchSuppliers = async () => {
        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`${API_URL}/suppliers`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.error || data.message || 'Failed to fetch suppliers.')
            }

            setSuppliers(data)
        } catch (error) {
            setError(error.message)
        }
    }

    // Fetch products
    const fetchProducts = async () => {
        try {
            const response = await fetch(`${API_URL}/inventory`)
            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.error || data.message || 'Failed to fetch products.')
            }

            setProducts(data)
        } catch (error) {
            setError(error.message)
        }
    }

    //Load suppliers and products on component mount
    useEffect(() => {
        fetchSuppliers()
        fetchProducts()
    }, [])

    const [formData, setFormData] = useState({
        supplier_id: '',
        product_id: '',
        quantity: '',
        date_of_order: ''
    })

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    const handleSubmit = (e) => {
        e.preventDefault()

        const newOrder = {
            id: Date.now(),
            ...formData,
            status: 'Pending'
        }

        setOrders([...orders, newOrder])

        setFormData({
            supplier_id: '',
            product_id: '',
            quantity: '',
            date_of_order: ''
        })
    }

    const handleApprove = (id) => {
        setOrders(orders.map((order) =>
            order.id === id
                ? { ...order, status: 'Approved' }
                : order
        ))
    }

    const handleCancel = (id) => {
        setOrders(orders.map((order) =>
            order.id === id
                ? { ...order, status: 'Cancelled' }
                : order
        ))
    }

    return (
        <div className="supply-orders-page">
            <h2>Supply Orders</h2>
            <p>View and manage your supply orders.</p>

            <form onSubmit={handleSubmit} className="order-form">
                <h3>Create Supply Order</h3>

                <select
                    name="supplier_id"
                    value={formData.supplier_id}
                    onChange={handleChange}
                    required
                >
                    <option value="">Select Supplier</option>
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
                    name="orderDate"
                    value={formData.orderDate}
                    onChange={handleChange}
                    required
                />

                <button type="submit">Create Order</button>
            </form>

            <div className="orders-list">
                <h3>All Supply Orders</h3>

                {orders.length === 0 ? (
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
                                    <td>{order.supplier}</td>
                                    <td>{order.product}</td>
                                    <td>{order.quantity}</td>
                                    <td>{order.orderDate}</td>
                                    <td>{order.status}</td>
                                    <td>
                                        {order.status === 'Pending' && (
                                            <>
                                                <button
                                                    onClick={() => handleApprove(order.id)}
                                                >
                                                    Approve
                                                </button>

                                                <button
                                                    onClick={() => handleCancel(order.id)}
                                                >
                                                    Cancel
                                                </button>
                                            </>
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

 
    