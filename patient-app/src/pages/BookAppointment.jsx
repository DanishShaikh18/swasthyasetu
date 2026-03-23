import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getDoctorSlots } from '../api/doctors'
import { bookAppointment } from '../api/patient'

export default function BookAppointment() {
  const { doctorId } = useParams()
  const [slots, setSlots] = useState([])
  const [selected, setSelected] = useState(null)
  const [complaint, setComplaint] = useState('')
  const [loading, setLoading] = useState(true)
  const [booking, setBooking] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { t } = useTranslation()

  useEffect(() => {
    getDoctorSlots(doctorId, { days: 7 }).then(r => {
      setSlots(r.data?.data || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [doctorId])

  const grouped = slots.reduce((acc, s) => {
    const d = new Date(s.slot_time).toLocaleDateString('en-IN', { weekday:'short', day:'numeric', month:'short' })
    if (!acc[d]) acc[d] = []; acc[d].push(s); return acc
  }, {})

  const handleBook = async () => {
    if (!selected) return
    setBooking(true); setError('')
    try {
      await bookAppointment({ doctor_id: doctorId, slot_time: selected.slot_time, chief_complaint: complaint })
      navigate('/prescriptions')
    } catch (err) {
      setError(err.response?.status === 409 ? 'Slot already taken. Please select another.' : 'Booking failed')
    } finally { setBooking(false) }
  }

  return (
    <div className="px-4 py-4">
      <button onClick={() => navigate(-1)} className="text-primary font-medium mb-3 min-h-[44px]">← {t('common.back')}</button>
      <h1 className="text-xl font-bold text-text-dark mb-4">{t('doctors.selectSlot')}</h1>

      {loading ? (
        <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-20 rounded-xl" />)}</div>
      ) : Object.keys(grouped).length === 0 ? (
        <p className="text-center text-text-muted py-8">{t('doctors.noSlots')}</p>
      ) : (
        Object.entries(grouped).map(([day, daySlots]) => (
          <div key={day} className="mb-4">
            <h3 className="text-sm font-semibold text-text-mid mb-2">{day}</h3>
            <div className="flex flex-wrap gap-2">
              {daySlots.map(s => (
                <button key={s.id} onClick={() => setSelected(s)}
                  className={`px-3 py-2 rounded-xl text-sm min-h-[44px] transition-all ${
                    selected?.id === s.id ? 'bg-primary text-white' : 'bg-surface border border-border text-text-dark hover:border-primary'
                  }`}>
                  {new Date(s.slot_time).toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit' })}
                </button>
              ))}
            </div>
          </div>
        ))
      )}

      {selected && (
        <div className="mt-4">
          <textarea value={complaint} onChange={e => setComplaint(e.target.value)} rows={2}
            placeholder="Describe your concern (optional)"
            className="w-full p-3 rounded-xl border border-border bg-surface text-sm mb-3" />
          {error && <p className="text-urgency-red text-sm mb-3">{error}</p>}
          <button onClick={handleBook} disabled={booking}
            className="w-full py-3 bg-primary text-white rounded-xl font-semibold min-h-[48px] disabled:opacity-50">
            {booking ? '...' : t('doctors.confirmBooking')}
          </button>
        </div>
      )}
    </div>
  )
}
