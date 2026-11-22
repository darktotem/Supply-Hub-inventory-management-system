import { useState, useEffect } from 'react'
import { getSupplyHistory } from '../../api/supply'
import './supply.css'

function History() {

    //Component state
    const [transactions, setTransactions] = useState([])
    const [searchTerm, setSearchTerm] = useState('')
    const [statusFilter, setStatusFilter] = useState('All')
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [page, setPage] = useState(1)
    const PAGE_SIZE = 8

    //Get supply history
    const fetchHistory = async () => {
        try {
            const data = await getSupplyHistory()
            setTransactions(data)
        } catch (error) {
            setError(error.message)
        } finally {
            setLoading(false)
        }
    }

    //Load history on component mount
    useEffect(() => {
        fetchHistory()
    }, [])

//Filter displayed records
const filteredTransactions = transactions.filter((transaction) => {
    const search = searchTerm.toLowerCase()

    const supplierName = transaction.supplier?.name || ''
    const productId = String(transaction.product_id || '')

    const matchesSearch =
        String(transaction.id).includes(search) ||
        supplierName.toLowerCase().includes(search) ||
        productId.includes(search)

    const matchesStatus =
        statusFilter === 'All' ||
        transaction.status.toLowerCase() === statusFilter.toLowerCase()

    return matchesSearch && matchesStatus
})

//Transaction status
const countByStatus = (status) =>
    transactions.filter((transaction) => transaction.status === status).length

//Pagination
const totalPages = Math.max(1, Math.ceil(filteredTransactions.length / PAGE_SIZE))
const currentPage = Math.min(page, totalPages)
const pagedTransactions = filteredTransactions.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
)
    return (
        <div className="history-page">
            <h2>Transaction History</h2>
            <p>View previous supply orders and transactions.</p>

            <div className="stat-cards">
                <div className="stat-card">
                    <div className="stat-header">
                        <span className="stat-icon stat-icon-total">📦</span>
                        <span className="stat-label">Total Transactions</span>
                    </div>
                    <span className="stat-value">{transactions.length}</span>
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

            <div className="filters">
                <input
                    type="text"
                    placeholder="Search by order ID, Supplier, or Product ID..."
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
                    <option value="Cancelled">Cancelled</option>
                    <option value ="Delivered">Delivered</option>
                </select>
            </div>

            <div className="transaction-list">
                <h3>Previous Supply Transactions</h3>

                {loading ? (
                    <p>Loading supply history...</p>
                ) : error ? (
                    <p className="error">{error}</p>
                ) : filteredTransactions.length === 0 ? (
                    <p>No supply history available.</p>
                ) : (
                                       <>
                        <table>
                            <thead>
                                <tr>
                                    <th>Order ID</th>
                                    <th>Supplier</th>
                                    <th>Product ID</th>
                                    <th>Quantity</th>
                                    <th>Order Date</th>
                                    <th>Delivery Date</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pagedTransactions.map((transaction) => (
                                    <tr key={transaction.id}>
                                        <td>#{transaction.id}</td>
                                        <td>{transaction.supplier?.name || 'Unknown'}</td>
                                        <td>{transaction.product_id}</td>
                                        <td>{transaction.quantity}</td>
                                        <td>{transaction.date_of_order}</td>
                                        <td>{transaction.date_of_delivery || '-'}</td>
                                        <td>
                                            <span className={`status-badge status-${transaction.status.toLowerCase()}`}>
                                                {transaction.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        <div className="pagination">
                            <span className="pagination-info">
                                Showing {(currentPage - 1) * PAGE_SIZE + 1}-
                                {Math.min(currentPage * PAGE_SIZE, filteredTransactions.length)} of {filteredTransactions.length} transactions
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

export default History
