import { useState, useEffect } from 'react'
import { getSuppliers, getInventory, getSupplyHistory,createSupplyOrder,cancelSupplyOrder,deliverSupplyOrder} from '../../api/supply'
import './supply.css'

function SupplyOrders() {
    const [orders, setOrders] = useState([])
    const [suppliers, setSuppliers] = useState([])
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)
    const [submitting, setSubmitting] = useState(false)
    const [cancelling, setCancelling] = useState(null)
    const [delivering, setDelivering] = useState(null)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const [searchTerm, setSearchTerm] = useState('')
    const [statusFilter, setStatusFilter] = useState('All')
    const [page, setPage] = useState(1)
    const PAGE_SIZE = 8

    //Fetch suppliers
    const fetchSuppliers = async () => {
        try {
            const data = await getSuppliers()
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
            const data = await getInventory()
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
            const data = await getSupplyHistory()
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
            await createSupplyOrder({
                supplier_id: Number(formData.supplier_id),
                product_id: Number(formData.product_id),
                quantity: Number(formData.quantity),
                date_of_order: formData.date_of_order
            })

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
            setCancelling(id)
            setSuccess('')

            await cancelSupplyOrder(id)

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
            setCancelling(null)
        }
    }

    // Mark Supply order as delivered
    const handleDeliver = async (id) => {
        try {
            setDelivering(id)
            setSuccess('')

            const today = new Date()
            const deliveryDate = [
                 today.getFullYear(),
                 String(today.getMonth() + 1).padStart(2, '0'),
                 String(today.getDate()).padStart(2, '0')
            ].join('-')

            await deliverSupplyOrder(id, deliveryDate)

            setOrders((previousOrders) => 
              previousOrders.map((order) =>
                order.id === id
                 ? { ...order, status: 'Delivered', date_of_delivery: deliveryDate }
                 : order
              )
            )

            setError('')
            setSuccess('Supply order marked as delivered successfully!')
        } catch (error) {
            setError(error.message)
        } finally {
            setDelivering(null)
        }
    }

    //Get product name
    const productName = (id) =>
        products.find((product) => product.id === id)?.product_name || String(id)

    //Count orders with a given status
    const countByStatus = (status) =>
        orders.filter((order) => order.status === status).length

    //Filter Orders
    const filteredOrders = orders.filter((order) => {
        const search = searchTerm.toLowerCase()
        const matchesSearch =
            String(order.id).includes(search) ||
            (order.supplier?.name || '').toLowerCase().includes(search) ||
            productName(order.product_id).toLowerCase().includes(search)
        const matchesStatus = statusFilter === 'All' || order.status === statusFilter
        return matchesSearch && matchesStatus
    })
 
    //Pagination
    const totalPages = Math.max(1, Math.ceil(filteredOrders.length / PAGE_SIZE))
    const currentPage = Math.min(page, totalPages)
    const pagedOrders = filteredOrders.slice(
        (currentPage - 1) * PAGE_SIZE,
        currentPage * PAGE_SIZE
    )

    return (
        <div className="supply-orders-page">
            <h2>Supply Orders</h2>
            <p>View and manage your supply orders.</p>
            {error && <p className="error-message">{error}</p>}
            {success && <p className="success-message">{success}</p>}

            
            <div className="stat-cards">
                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon stat-icon-total">📦</span>
                        <span className="stat-label">Total Orders</span>
                    </div>
                    <span className="stat-value">{orders.length}</span>
                    <span className="stat-badge stat-badge-total">All supply orders</span>
                </div>

                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon stat-icon-pending">⏳</span>
                        <span className="stat-label">Pending</span>
                    </div>
                    <span className="stat-value">{countByStatus('Pending')}</span>
                    <span className="stat-badge stat-badge-pending">Awaiting delivery</span>
                </div>

                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon stat-icon-delivered">✅</span>
                        <span className="stat-label">Delivered</span>
                    </div>
                    <span className="stat-value">{countByStatus('Delivered')}</span>
                    <span className="stat-badge stat-badge-delivered">Received</span>
                </div>

                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon stat-icon-cancelled">✖</span>
                        <span className="stat-label">Cancelled</span>
                    </div>
                    <span className="stat-value">{countByStatus('Cancelled')}</span>
                    <span className="stat-badge stat-badge-cancelled">Order cancelled</span>
                </div>
            </div>

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
                    onClick={(e) => e.target.showPicker?.()}
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

                <div className="filters">
                    <input
                        type="text"
                        placeholder="Search by order ID, supplier or product..."
                        value={searchTerm}
                        onChange={(e) => {
                            setSearchTerm(e.target.value)
                            setPage(1)
                        }}
                    />

                    <select
                        value={statusFilter}
                        onChange={(e) => {
                            setStatusFilter(e.target.value)
                            setPage(1)
                        }}
                    >
                        <option value="All">All Statuses</option>
                        <option value="Pending">Pending</option>
                        <option value="Delivered">Delivered</option>
                        <option value="Cancelled">Cancelled</option>
                    </select>
                </div>

                {loading ? (
                    <p>Loading supply orders...</p>
                ) : filteredOrders.length === 0 ? (
                    <p>No supply orders found.</p>
                ) : (
                    <>
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
                                {pagedOrders.map((order) => (
                                    <tr key={order.id}>
                                        <td>#{order.id}</td>
                                        <td>{order.supplier?.name}</td>
                                        <td>{productName(order.product_id)}</td>
                                        <td>{order.quantity}</td>
                                        <td>{order.date_of_order}</td>
                                        <td>
                                            <span className={`status-badge status-${order.status.toLowerCase()}`}>
                                                {order.status}
                                            </span>
                                        </td>
                                        <td>
                                            {order.status === 'Pending' && (
                                                <>
                                                    <button
                                                        type="button"
                                                        className="cancel-btn"
                                                        onClick={() => handleCancel(order.id)}
                                                        disabled={cancelling === order.id || delivering === order.id}
                                                    >
                                                        {cancelling === order.id ? 'Cancelling...' : 'Cancel'}
                                                    </button>

                                                    <button
                                                         type="button"
                                                         onClick={() => handleDeliver(order.id)}
                                                         disabled={cancelling === order.id || delivering === order.id}
                                                    >
                                                         {delivering === order.id ? 'Updating...' : 'Mark as Delivered'}
                                                    </button>
                                                </>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        <div className="pagination">
                            <span className="pagination-info">
                                Showing {(currentPage - 1) * PAGE_SIZE + 1}-
                                {Math.min(currentPage * PAGE_SIZE, filteredOrders.length)} of {filteredOrders.length} orders
                            </span>

                            <div className="pagination-buttons">
                                <button
                                    type="button"
                                    onClick={() => setPage(currentPage - 1)}
                                    disabled={currentPage === 1}
                                >
                                    &lt;
                                </button>

                                {Array.from({ length: totalPages }, (_, index) => index + 1).map((number) => (
                                    <button
                                        type="button"
                                        key={number}
                                        className={number === currentPage ? 'active' : ''}
                                        onClick={() => setPage(number)}
                                    >
                                        {number}
                                    </button>
                                ))}

                                <button
                                    type="button"
                                    onClick={() => setPage(currentPage + 1)}
                                    disabled={currentPage === totalPages}
                                >
                                    &gt;
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>
           
        </div>
    )
}

export default SupplyOrders

 
    