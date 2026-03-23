import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { getAppointments, updateAvailability } from '../api'

export default function Dashboard() {
  const user = useAuthStore(s => s.user)
  const [appointments, setAppointments] = useState([])
  const [isAvailable, setIsAvailable] = useState(true)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getAppointments({ status: 'pending', page: 1, limit: 20 }).then(r => {
      setAppointments(r.data?.data?.items || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const toggleAvailability = async () => {
    try {
      await updateAvailability({ is_available: !isAvailable })
      setIsAvailable(!isAvailable)
    } catch {}
  }

  const today = appointments.filter(a => {
    const d = new Date(a.scheduled_at)
    return d.toDateString() === new Date().toDateString()
  })
  const pending = appointments.filter(a => a.status === 'pending')

  return (
    <div className="p-6 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-text-dark">Welcome, {user?.fullName}</h1>
          <p className="text-text-mid text-sm mt-1">Doctor Dashboard</p>
        </div>
        <button onClick={toggleAvailability}
          className={`px-4 py-2 rounded-xl text-sm font-medium min-h-[40px] transition-colors ${isAvailable ? 'bg-urgency-green text-white' : 'bg-gray-200 text-text-muted'}`}>
          {isAvailable ? '● Online' : '○ Offline'}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {[
          { l: "Today's Appointments", v: today.length, icon: '📅' },
          { l: 'Pending Requests', v: pending.length, icon: '⏳' },
          { l: 'Status', v: isAvailable ? 'Online' : 'Offline', icon: '🟢' },
          { l: 'Total Patients', v: appointments.length, icon: '👥' },
        ].map(s => (
          <div key={s.l} className="bg-surface rounded-2xl p-4 border border-border">
            <span className="text-2xl">{s.icon}</span>
            <p className="text-2xl font-bold text-text-dark mt-2">{s.v}</p>
            <p className="text-xs text-text-muted">{s.l}</p>
          </div>
        ))}
      </div>

      {/* Pending Appointments */}
      <h2 className="text-lg font-semibold mb-3">Pending Appointments</h2>
      {loading ? (
        <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 bg-gray-100 rounded-2xl animate-pulse" />)}</div>
      ) : pending.length === 0 ? (
        <p className="text-text-muted py-4">No pending appointments</p>
      ) : (
        <div className="space-y-3">
          {pending.map(a => (
            <div key={a.id} className="bg-surface rounded-2xl p-4 border border-border flex items-center justify-between">
              <div>
                <p className="font-medium">{a.patient_name}</p>
                <p className="text-sm text-text-mid">{a.chief_complaint || 'General consultation'}</p>
                <p className="text-xs text-text-muted">{new Date(a.scheduled_at).toLocaleString('en-IN')}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => navigate(`/patient/${a.patient_id}`)}
                  className="px-3 py-2 bg-primary-light text-primary rounded-xl text-sm font-medium min-h-[40px]">
                  View
                </button>
                <button onClick={() => navigate('/appointments')}
                  className="px-3 py-2 bg-primary text-white rounded-xl text-sm font-medium min-h-[40px]">
                  Accept
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
