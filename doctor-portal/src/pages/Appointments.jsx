import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getAppointments, updateAppointment, joinVideoCall } from '../api'

export default function Appointments() {
  const [appointments, setAppointments] = useState([])
  const [tab, setTab] = useState('pending')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => { fetchAppointments() }, [tab])

  const fetchAppointments = async () => {
    setLoading(true)
    try {
      const res = await getAppointments({ status: tab, page: 1, limit: 50 })
      setAppointments(res.data?.data?.items || [])
    } catch {} finally { setLoading(false) }
  }

  const handleAction = async (id, status) => {
    try {
      await updateAppointment(id, { status })
      fetchAppointments()
    } catch {}
  }

  const handleJoin = async (id) => {
    try {
      const res = await joinVideoCall(id)
      window.open(res.data?.data?.room_url, '_blank')
    } catch (err) { alert(err.response?.data?.detail || 'Cannot join call') }
  }

  const tabs = ['pending', 'confirmed', 'completed', 'cancelled']

  return (
    <div className="p-6 max-w-4xl">
      <h1 className="text-2xl font-bold mb-4">Appointments</h1>
      <div className="flex gap-2 mb-4 overflow-x-auto">
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-xl text-sm font-medium min-h-[40px] capitalize transition-colors ${tab === t ? 'bg-primary text-white' : 'bg-surface border border-border text-text-mid'}`}>
            {t}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 bg-gray-100 rounded-2xl animate-pulse" />)}</div>
      ) : appointments.length === 0 ? (
        <p className="text-text-muted py-8 text-center">No {tab} appointments</p>
      ) : (
        <div className="space-y-3">
          {appointments.map(a => (
            <div key={a.id} className="bg-surface rounded-2xl p-4 border border-border">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold">{a.patient_name}</p>
                  <p className="text-sm text-text-mid">{a.chief_complaint || 'General consultation'}</p>
                  <p className="text-xs text-text-muted mt-1">{new Date(a.scheduled_at).toLocaleString('en-IN')}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${a.status === 'confirmed' ? 'bg-urgency-green text-white' : a.status === 'pending' ? 'bg-urgency-yellow text-white' : 'bg-gray-200 text-text-muted'}`}>
                  {a.status}
                </span>
              </div>
              <div className="flex gap-2 mt-3 flex-wrap">
                {a.status === 'pending' && (<>
                  <button onClick={() => handleAction(a.id, 'confirmed')} className="px-3 py-2 bg-urgency-green text-white rounded-xl text-sm min-h-[40px]">✓ Accept</button>
                  <button onClick={() => handleAction(a.id, 'cancelled')} className="px-3 py-2 bg-urgency-red text-white rounded-xl text-sm min-h-[40px]">✕ Reject</button>
                </>)}
                {a.status === 'confirmed' && (
                  <button onClick={() => handleJoin(a.id)} className="px-3 py-2 bg-primary text-white rounded-xl text-sm min-h-[40px]">📹 Start Call</button>
                )}
                <button onClick={() => navigate(`/patient/${a.patient_id}`)} className="px-3 py-2 bg-primary-light text-primary rounded-xl text-sm min-h-[40px]">View Patient</button>
                {a.status === 'confirmed' && (
                  <button onClick={() => navigate(`/prescribe/${a.id}`)} className="px-3 py-2 bg-surface border border-primary text-primary rounded-xl text-sm min-h-[40px]">Write Rx</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
