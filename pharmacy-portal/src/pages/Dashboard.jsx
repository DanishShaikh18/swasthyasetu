import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { getProfile, toggleStatus, getInventory } from '../api'

export default function Dashboard() {
  const user = useAuthStore(s => s.user)
  const [profile, setProfile] = useState(null)
  const [stats, setStats] = useState({ total: 0, lowStock: 0, outOfStock: 0 })
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      getProfile().then(r => setProfile(r.data?.data)),
      getInventory({ page: 1, limit: 500 }).then(r => {
        const items = r.data?.data?.items || []
        setStats({
          total: items.length,
          lowStock: items.filter(i => i.quantity_in_stock > 0 && i.quantity_in_stock < 20).length,
          outOfStock: items.filter(i => i.quantity_in_stock === 0).length,
        })
      })
    ]).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleToggle = async () => {
    const newStatus = !profile?.is_open_now
    try {
      await toggleStatus({ is_open_now: newStatus })
      setProfile(p => ({ ...p, is_open_now: newStatus }))
    } catch {}
  }

  if (loading) return <div className="p-6"><div className="h-40 bg-amber-50 rounded-2xl animate-pulse" /></div>

  return (
    <div className="p-6 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-text-dark">Welcome, {profile?.pharmacy_name || user?.fullName}</h1>
          <p className="text-text-mid text-sm mt-1">{profile?.address}</p>
        </div>
        <button onClick={handleToggle}
          className={`px-5 py-2.5 rounded-xl text-sm font-semibold min-h-[44px] transition-all ${
            profile?.is_open_now ? 'bg-success text-white' : 'bg-gray-200 text-text-muted'
          }`}>
          {profile?.is_open_now ? '🟢 Open Now' : '🔴 Closed'}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {[
          { label: 'Total Medicines', value: stats.total, icon: '💊', color: 'bg-primary-light text-primary' },
          { label: 'Low Stock', value: stats.lowStock, icon: '⚠️', color: 'bg-yellow-50 text-warning' },
          { label: 'Out of Stock', value: stats.outOfStock, icon: '❌', color: 'bg-red-50 text-danger' },
          { label: 'Status', value: profile?.is_open_now ? 'Open' : 'Closed', icon: '🏪', color: 'bg-green-50 text-success' },
        ].map(s => (
          <div key={s.label} className="bg-surface rounded-2xl p-4 border border-border">
            <span className="text-2xl">{s.icon}</span>
            <p className="text-2xl font-bold text-text-dark mt-2">{s.value}</p>
            <p className="text-xs text-text-muted">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <h2 className="text-lg font-semibold mb-3">Quick Actions</h2>
      <div className="grid grid-cols-2 gap-3">
        <button onClick={() => navigate('/inventory')}
          className="bg-surface rounded-2xl p-5 border border-border shadow-sm hover:shadow-md hover:border-primary/30 transition-all flex flex-col items-center gap-2 min-h-[100px]">
          <span className="text-3xl">💊</span>
          <span className="text-sm font-medium">Manage Inventory</span>
        </button>
        <button onClick={() => navigate('/upload')}
          className="bg-surface rounded-2xl p-5 border border-border shadow-sm hover:shadow-md hover:border-primary/30 transition-all flex flex-col items-center gap-2 min-h-[100px]">
          <span className="text-3xl">📤</span>
          <span className="text-sm font-medium">Bulk Upload CSV</span>
        </button>
      </div>

      {/* Low stock alert */}
      {stats.lowStock > 0 && (
        <div className="mt-6 bg-yellow-50 border border-warning/30 rounded-2xl p-4">
          <h3 className="font-semibold text-warning text-sm">⚠️ Low Stock Alert</h3>
          <p className="text-sm text-text-mid mt-1">{stats.lowStock} medicines have less than 20 units in stock.</p>
          <button onClick={() => navigate('/inventory?filter=low')}
            className="mt-2 text-sm text-primary font-medium">View Low Stock Items →</button>
        </div>
      )}
    </div>
  )
}
