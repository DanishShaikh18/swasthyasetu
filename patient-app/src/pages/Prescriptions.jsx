import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { getPrescriptions } from '../api/patient'
import PrescriptionCard from '../components/PrescriptionCard'

export default function Prescriptions() {
  const [prescriptions, setPrescriptions] = useState([])
  const [loading, setLoading] = useState(true)
  const { t } = useTranslation()

  useEffect(() => {
    getPrescriptions({ page: 1, limit: 50 }).then(r => {
      setPrescriptions(r.data?.data?.items || [])
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  return (
    <div className="px-4 py-4">
      <h1 className="text-xl font-bold text-text-dark mb-4">{t('prescriptions.title')}</h1>
      {loading ? (
        <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-24 rounded-2xl" />)}</div>
      ) : prescriptions.length === 0 ? (
        <p className="text-center text-text-muted py-8">{t('common.noData')}</p>
      ) : (
        <div className="space-y-3">
          {prescriptions.map(rx => <PrescriptionCard key={rx.id} prescription={rx} />)}
        </div>
      )}
    </div>
  )
}
