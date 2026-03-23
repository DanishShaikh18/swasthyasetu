import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { listDoctors } from '../api/doctors'
import DoctorCard from '../components/DoctorCard'

export default function Doctors() {
  const [doctors, setDoctors] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [availableOnly, setAvailableOnly] = useState(false)
  const navigate = useNavigate()
  const { t } = useTranslation()

  useEffect(() => {
    fetchDoctors()
  }, [filter, availableOnly])

  const fetchDoctors = async () => {
    setLoading(true)
    try {
      const params = { page: 1, limit: 50 }
      if (filter) params.specialization = filter
      if (availableOnly) params.available_now = true
      const res = await listDoctors(params)
      setDoctors(res.data?.data?.items || [])
    } catch { setDoctors([]) }
    finally { setLoading(false) }
  }

  const specializations = ['', 'General Physician', 'Pediatrician', 'Cardiologist', 'Dermatologist', 'Gynecologist', 'Orthopedic', 'Psychiatrist', 'ENT', 'Ophthalmologist']

  return (
    <div className="px-4 py-4">
      <h1 className="text-xl font-bold text-text-dark mb-3">{t('doctors.title')}</h1>

      {/* Filters */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        <select value={filter} onChange={e => setFilter(e.target.value)}
          className="p-2.5 rounded-xl border border-border bg-surface text-sm min-h-[44px] flex-shrink-0">
          <option value="">{t('doctors.specialization')}</option>
          {specializations.filter(Boolean).map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <button onClick={() => setAvailableOnly(!availableOnly)}
          className={`px-4 py-2 rounded-xl text-sm font-medium min-h-[44px] flex-shrink-0 transition-colors ${
            availableOnly ? 'bg-primary text-white' : 'bg-surface border border-border text-text-mid'
          }`}>
          ● {t('doctors.available')}
        </button>
      </div>

      {/* Doctor List */}
      {loading ? (
        <div className="space-y-3">
          {[1,2,3].map(i => <div key={i} className="skeleton h-36 rounded-2xl" />)}
        </div>
      ) : (
        <div className="space-y-3">
          {doctors.length === 0 && <p className="text-center text-text-muted py-8">{t('common.noData')}</p>}
          {doctors.map(doc => (
            <DoctorCard key={doc.id} doctor={doc} onBook={() => navigate(`/book/${doc.id}`)} />
          ))}
        </div>
      )}
    </div>
  )
}
