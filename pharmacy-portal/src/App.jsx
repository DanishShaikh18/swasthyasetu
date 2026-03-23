import { Routes, Route, Navigate, NavLink } from 'react-router-dom'
import useAuthStore from './store/authStore'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Inventory from './pages/Inventory'
import BulkUpload from './pages/BulkUpload'
import Profile from './pages/Profile'

function ProtectedRoute({ children }) {
  return useAuthStore(s => s.isAuthenticated) ? children : <Navigate to="/login" />
}

function Sidebar() {
  const links = [
    { to: '/', icon: '📊', label: 'Dashboard' },
    { to: '/inventory', icon: '💊', label: 'Inventory' },
    { to: '/upload', icon: '📤', label: 'Bulk Upload' },
    { to: '/profile', icon: '👤', label: 'Profile' },
  ]
  return (
    <aside className="hidden md:flex flex-col w-56 bg-sidebar text-white min-h-screen p-4 gap-1">
      <h1 className="text-lg font-bold mb-6 px-2">💊 Pharmacy Portal</h1>
      {links.map(l => (
        <NavLink key={l.to} to={l.to} end={l.to === '/'}
          className={({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors ${isActive ? 'bg-primary text-white font-medium' : 'text-amber-200 hover:text-white hover:bg-white/10'}`}>
          <span>{l.icon}</span><span>{l.label}</span>
        </NavLink>
      ))}
    </aside>
  )
}

function MobileNav() {
  const links = [
    { to: '/', icon: '📊', label: 'Home' },
    { to: '/inventory', icon: '💊', label: 'Inventory' },
    { to: '/upload', icon: '📤', label: 'Upload' },
    { to: '/profile', icon: '👤', label: 'Profile' },
  ]
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-surface border-t border-border z-50">
      <div className="flex justify-around">
        {links.map(l => (
          <NavLink key={l.to} to={l.to} end={l.to === '/'}
            className={({ isActive }) => `flex flex-col items-center py-2 px-2 text-xs ${isActive ? 'text-primary font-semibold' : 'text-text-muted'}`}>
            <span className="text-lg">{l.icon}</span><span>{l.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}

export default function App() {
  const isAuth = useAuthStore(s => s.isAuthenticated)
  return (
    <div className="flex min-h-screen bg-background">
      {isAuth && <Sidebar />}
      <main className={`flex-1 ${isAuth ? 'pb-16 md:pb-0' : ''}`}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/inventory" element={<ProtectedRoute><Inventory /></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute><BulkUpload /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      {isAuth && <MobileNav />}
    </div>
  )
}
