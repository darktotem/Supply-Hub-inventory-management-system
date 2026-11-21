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

    return (
        <div className="history-page">
            <h2>Transaction History</h2>
            <p>View previous supply orders and transactions.</p>

            <div className="filters">
                <input
                    type="text"
                    placeholder="Search by order ID, Supplier, or Product ID..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />

                <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
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
                            {filteredTransactions.map((transaction) => (
                                <tr key={transaction.id}>
                                    <td>{transaction.id}</td>
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
                )}
            </div>
        </div>
    )
}

export default History
