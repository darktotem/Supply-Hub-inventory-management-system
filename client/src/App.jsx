import { BrowserRouter, Routes, Route } from 'react-router-dom'

import AppLayout from './components/AppLayout'

// Dashboard
import Dashboard from './features/admin/dashboard'

// Inventory
import Inventory from './features/inventory/inventory'

function NotFound() {
  return <h1>404 - Page Not Found</h1>
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/inventory" element={<Inventory />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App