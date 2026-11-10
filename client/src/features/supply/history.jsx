import { useState } from 'react'

function History({ transactions = [] }) {
    const [searchTerm, setSearchTerm] = useState('')
    const [statusFilter, setStatusFilter] = useState('All')

    const filteredTransactions = transactions.filter((transaction) => {
        const search = searchTerm.toLowerCase()

        const matchesSearch = 
        transaction.id.toString().toLowerCase().includes(search) ||
        transaction.supplier.toLowerCase().includes(search) ||
        transaction.product.toLowerCase().includes(search)

        const matchesStatus = 
        statusFilter === 'All' || transaction.status.toLowerCase() === statusFilter.toLowerCase()

        return matchesSearch && matchesStatus
        
    })

    return (
        <div className="history-page">
            <h2>Transaction History</h2>
            <p>View previous supply orders and transactions.</p>

            <div className="filters">
                <input
                    type="text"
                    placeholder="Search by order ID, Supplier, or Product..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />

                <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                >
                    <option value="All">All Statuses</option>
                    <option value="Pending">Pending</option>
                    <option value="Approved">Approved</option>
                    <option value="Cancelled">Cancelled</option>
                    <option value ="Delivered">Delivered</option>
                </select>
            </div>

            <div className="transaction-list">
                <h3>Previous Supply Transactions</h3>

                {filteredTransactions.length === 0 ? (
                    <p>No supply history available.</p>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Supplier</th>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Date</th>
                                <th>Total Cost</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredTransactions.map((transaction) => (
                                <tr key={transaction.id}>
                                    <td>{transaction.id}</td>
                                    <td>{transaction.supplier}</td>
                                    <td>{transaction.product}</td>
                                    <td>{transaction.quantity}</td>
                                    <td>{transaction.orderDate}</td>
                                    <td>
                                        {transaction.cost !== null &&
                                        transaction.cost !== undefined &&
                                        transaction.cost !== "" 
                                            ? `KES ${Number(transaction.cost).toLocaleString()}`
                                            : '-'}
                                    </td>
                                    <td>{transaction.status}</td>
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
