
const summaryCards = [
  {
    title: 'Total Products',
    value: '1,248',
    change: '+12.5%',
    description: 'Compared to last month',
    icon: '▦',
  },
  {
    title: 'Stock Value',
    value: 'KES 845,200',
    change: '+8.2%',
    description: 'Current inventory value',
    icon: '◈',
  },
  {
    title: 'Low Stock Items',
    value: '18',
    change: 'Needs attention',
    description: 'Products below threshold',
    icon: '⚠',
  },
  {
    title: 'Total Suppliers',
    value: '64',
    change: '+4 new',
    description: 'Registered suppliers',
    icon: '♧',
  },
]

const lowStockItems = [
  { name: 'Wireless Mouse', category: 'Electronics', quantity: 4, threshold: 10 },
  { name: 'Office Paper A4', category: 'Stationery', quantity: 8, threshold: 20 },
  { name: 'USB Keyboard', category: 'Electronics', quantity: 3, threshold: 10 },
  { name: 'Printer Ink', category: 'Accessories', quantity: 2, threshold: 8 },
]

const recentActivity = [
  { action: 'New stock added', item: 'Wireless Mouse', date: 'Today, 10:45 AM', status: 'Completed' },
  { action: 'Purchase order created', item: 'Office Supplies', date: 'Today, 09:30 AM', status: 'Pending' },
  { action: 'Sale completed', item: 'USB Keyboard', date: 'Yesterday, 04:15 PM', status: 'Completed' },
  { action: 'Supplier registered', item: 'Tech Solutions Ltd', date: 'Yesterday, 11:20 AM', status: 'Completed' },
]

function Dashboard() {
  return (
    <div className="dashboard">
      <div className="page-heading">
        <div>
          <h1>Dashboard</h1>
          <p>Welcome back! Here's what's happening with your business today.</p>
        </div>

        <button className="primary-button">+ Add New Product</button>
      </div>

      <div className="summary-grid">
        {summaryCards.map((card) => (
          <div className="summary-card" key={card.title}>
            <div className="summary-card-top">
              <span>{card.title}</span>
              <span className="summary-icon">{card.icon}</span>
            </div>

            <h2>{card.value}</h2>
            <div className="summary-card-bottom">
              <strong>{card.change}</strong>
              <span>{card.description}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        <section className="dashboard-panel">
          <div className="panel-heading">
            <div>
              <h3>Low Stock Alerts</h3>
              <p>Products that need restocking</p>
            </div>
            <span className="alert-count">4 Alerts</span>
          </div>

          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Category</th>
                  <th>Quantity</th>
                  <th>Threshold</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {lowStockItems.map((item) => (
                  <tr key={item.name}>
                    <td>{item.name}</td>
                    <td>{item.category}</td>
                    <td>{item.quantity}</td>
                    <td>{item.threshold}</td>
                    <td><span className="status-badge low">Low Stock</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="dashboard-panel activity-panel">
          <div className="panel-heading">
            <div>
              <h3>Recent Activity</h3>
              <p>Latest business updates</p>
            </div>
          </div>

          <div className="activity-list">
            {recentActivity.map((activity, index) => (
              <div className="activity-item" key={index}>
                <div className="activity-marker"></div>
                <div className="activity-details">
                  <strong>{activity.action}</strong>
                  <span>{activity.item}</span>
                  <small>{activity.date}</small>
                </div>
                <span className={`status-badge ${activity.status === 'Pending' ? 'pending' : 'completed'}`}>
                  {activity.status}
                </span>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

export default Dashboard
