import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getPatientRecord } from '../api'

export default function PatientView() {
  const { patientId } = useParams()
  const [patient, setPatient] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getPatientRecord(patientId).then(r => setPatient(r.data?.data)).catch(() => {}).finally(() => setLoading(false))
  }, [patientId])

  if (loading) return <div className="p-6"><div className="h-40 bg-gray-100 rounded-2xl animate-pulse" /></div>
  if (!patient) return <div className="p-6 text-text-muted">Patient not found</div>

  return (
    <div className="p-6 max-w-3xl">
      <button onClick={() => navigate(-1)} className="text-primary font-medium mb-4 min-h-[40px]">← Back</button>
      <h1 className="text-2xl font-bold mb-4">{patient.full_name}</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-surface rounded-2xl p-4 border border-border">
          <h3 className="font-semibold text-text-mid text-sm mb-3">Personal Info</h3>
          {[
            ['Age', patient.age], ['Gender', patient.gender], ['Blood Group', patient.blood_group],
            ['Phone', patient.phone], ['Village', patient.village], ['District', patient.district], ['State', patient.state],
          ].map(([l, v]) => (
            <div key={l} className="flex justify-between py-1.5 text-sm">
              <span className="text-text-muted">{l}</span><span className="font-medium">{v || '—'}</span>
            </div>
          ))}
        </div>
        <div className="bg-surface rounded-2xl p-4 border border-border">
          <h3 className="font-semibold text-text-mid text-sm mb-3">Medical Info</h3>
          <div className="mb-3">
            <span className="text-xs text-text-muted block mb-1">Allergies</span>
            <div className="flex flex-wrap gap-1">
              {(patient.allergies || []).length ? patient.allergies.map(a => <span key={a} className="text-xs bg-urgency-red/10 text-urgency-red px-2 py-1 rounded-full">{a}</span>) : <span className="text-sm text-text-muted">None</span>}
            </div>
          </div>
          <div>
            <span className="text-xs text-text-muted block mb-1">Chronic Conditions</span>
            <div className="flex flex-wrap gap-1">
              {(patient.chronic_conditions || []).length ? patient.chronic_conditions.map(c => <span key={c} className="text-xs bg-urgency-yellow/10 text-urgency-yellow px-2 py-1 rounded-full">{c}</span>) : <span className="text-sm text-text-muted">None</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Past Prescriptions */}
      <h2 className="text-lg font-semibold mt-6 mb-3">Past Prescriptions</h2>
      {(patient.prescriptions || []).length === 0 ? (
        <p className="text-text-muted">No past prescriptions</p>
      ) : (
        <div className="space-y-3">
          {patient.prescriptions.map(rx => (
            <div key={rx.id} className="bg-surface rounded-2xl p-4 border border-border">
              <p className="font-medium">{rx.diagnosis}</p>
              <p className="text-sm text-text-mid mt-1">{(rx.medicines || []).map(m => m.name).join(', ')}</p>
              <p className="text-xs text-text-muted mt-1">{new Date(rx.created_at).toLocaleDateString('en-IN')}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
