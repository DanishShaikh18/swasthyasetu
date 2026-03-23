import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function PrescriptionCard({ prescription }) {
  const [expanded, setExpanded] = useState(false)
  const navigate = useNavigate()
  const { t } = useTranslation()

  return (
    <div className="bg-surface rounded-2xl border border-border shadow-sm overflow-hidden">
      <button onClick={() => setExpanded(!expanded)}
        className="w-full p-4 text-left min-h-[48px]">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-semibold text-text-dark">{prescription.doctor_name}</h3>
            <p className="text-sm text-primary">{prescription.diagnosis || 'Consultation'}</p>
          </div>
          <span className="text-xs text-text-muted bg-primary-light px-2 py-1 rounded-full">
            {new Date(prescription.created_at).toLocaleDateString('en-IN')}
          </span>
        </div>
      </button>

      {expanded && (
        <div className="px-4 pb-4 border-t border-border pt-3">
          <h4 className="text-sm font-semibold text-text-mid mb-2">{t('prescriptions.medicines')}</h4>
          {(prescription.medicines || []).map((med, i) => (
            <div key={i} className="mb-3 p-3 bg-primary-light/50 rounded-xl">
              <button onClick={() => navigate(`/medicine?search=${encodeURIComponent(med.name)}`)}
                className="font-medium text-primary text-sm underline-offset-2 hover:underline text-left min-h-[32px]">
                💊 {med.name}
              </button>
              <div className="text-xs text-text-mid mt-1 grid grid-cols-2 gap-1">
                {med.dosage && <span>{t('prescriptions.dosage')}: {med.dosage}</span>}
                {med.frequency && <span>{t('prescriptions.frequency')}: {med.frequency}</span>}
                {med.duration_days && <span>{t('prescriptions.duration')}: {med.duration_days} days</span>}
                {med.instructions && <span className="col-span-2">{med.instructions}</span>}
              </div>
            </div>
          ))}
          {prescription.advice && (
            <p className="text-sm text-text-mid mt-2">💡 {prescription.advice}</p>
          )}
          {prescription.follow_up_date && (
            <p className="text-sm text-urgency-yellow font-medium mt-2">
              📅 {t('prescriptions.followUp')}: {prescription.follow_up_date}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
