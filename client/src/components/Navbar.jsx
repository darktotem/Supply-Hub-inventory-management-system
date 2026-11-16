
import { useState } from 'react'

const navigation = [
  {
    title: 'OVERVIEW',
    links: [
      { label: 'Dashboard', icon: '◫' },
    ],
  },
  {
    title: 'MANAGEMENT',
    links: [
      { label: 'Inventory', icon: '▦' },
      { label: 'Suppliers', icon: '♧' },
      { label: 'Purchase Orders', icon: '▤' },
      { label: 'Deliveries', icon: '⇄' },
      { label: 'Sales', icon: '↗' },
      { label: 'Customers', icon: '♙' },
    ],
  },
  {
    title: 'BUSINESS',
    links: [
      { label: 'Invoices', icon: '▧' },
      { label: 'Payments', icon: '▣' },
      { label: 'Employees', icon: '♧' },
      { label: 'Audit Logs', icon: '◷' },
    ],
  },
  {
    title: 'SYSTEM',
    links: [
      { label: 'Settings', icon: '⚙' },
    ],
  },
]

/**
 * @param {{
 *   activePage: string,
 *   onNavigate: (page: string) => void,
 *   children: import('react').ReactNode
 * }} props
 */
export function Navbar({ activePage, onNavigate, children }) {
  const [search, setSearch] = useState('')

  return (
    <div className="app-layout">

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">S</div>
          <div>
            <h2>Supply Hub</h2>
            <span>BUSINESS MANAGEMENT</span>
          </div>
        </div>

        <nav className="sidebar-navigation">
          {navigation.map((section) => (
            <div className="nav-section" key={section.title}>
              <p className="nav-section-title">{section.title}</p>

              {section.links.map((link) => (
                <button
                  key={link.label}
                  className={`nav-link ${
                    activePage === link.label ? 'active' : ''
                  }`}
                  onClick={() => onNavigate(link.label)}
                >
                  <span className="nav-icon">{link.icon}</span>
                  <span>{link.label}</span>
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="help-icon">?</div>
          <div>
            <strong>Need help?</strong>
            <span>Contact your administrator</span>
          </div>
        </div>
      </aside>

      <div className="main-wrapper">

        <header className="topbar">
          <div className="breadcrumb">
            <span>Supply Hub</span>
            <span>/</span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-actions">
            <div className="search-box">
              <span>⌕</span>
              <input
                type="text"
                placeholder="Search anything..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
              <kbd>⌘ K</kbd>
            </div>

            <button className="notification-button" aria-label="Notifications">
              ♧
              <span className="notification-dot"></span>
            </button>

            <div className="profile">
              <div className="profile-avatar">AD</div>
              <div className="profile-info">
                <strong>Admin User</strong>
                <span>Administrator</span>
              </div>
              <span className="profile-arrow">⌄</span>
            </div>
          </div>
        </header>

        <main className="page-content">
          {children}
        </main>

      </div>
    </div>
  )
}
