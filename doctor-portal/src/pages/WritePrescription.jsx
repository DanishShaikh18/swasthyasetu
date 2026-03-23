import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { writePrescription } from '../api'

export default function WritePrescription() {
  const { appointmentId } = useParams()
  const navigate = useNavigate()
  const [diagnosis, setDiagnosis] = useState('')
  const [advice, setAdvice] = useState('')
  const [followUp, setFollowUp] = useState('')
  const [medicines, setMedicines] = useState([{ name:'', dosage:'', frequency:'', duration_days:5, instructions:'' }])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const addMed = () => setMedicines([...medicines, { name:'', dosage:'', frequency:'', duration_days:5, instructions:'' }])
  const removeMed = (i) => setMedicines(medicines.filter((_, idx) => idx !== i))
  const updateMed = (i, k, v) => { const m = [...medicines]; m[i][k] = v; setMedicines(m) }

  const handleSubmit = async () => {
    if (!diagnosis || !medicines[0]?.name) { setError('Diagnosis and at least 1 medicine required'); return }
    setLoading(true); setError('')
    try {
      await writePrescription({
        appointment_id: appointmentId, diagnosis, advice,
        follow_up_date: followUp || null,
        medicines: medicines.filter(m => m.name.trim()),
      })
      navigate('/appointments')
    } catch (err) { setError(err.response?.data?.detail?.error?.message || 'Failed to save') }
    finally { setLoading(false) }
  }

  return (
    <div className="p-6 max-w-3xl">
      <button onClick={() => navigate(-1)} className="text-primary font-medium mb-4 min-h-[40px]">← Back</button>
      <h1 className="text-2xl font-bold mb-4">Write Prescription</h1>

      <div className="bg-surface rounded-2xl p-5 border border-border">
        <div className="mb-4">
          <label className="text-sm font-medium text-text-mid mb-1 block">Diagnosis *</label>
          <input value={diagnosis} onChange={e => setDiagnosis(e.target.value)} placeholder="e.g. Viral Fever"
            className="w-full p-3 rounded-xl border border-border bg-background" />
        </div>

        <h3 className="font-semibold text-text-mid mb-3">Medicines</h3>
        {medicines.map((med, i) => (
          <div key={i} className="mb-4 p-3 bg-primary-light/30 rounded-xl relative">
            {medicines.length > 1 && (
              <button onClick={() => removeMed(i)} className="absolute top-2 right-2 text-urgency-red text-sm">✕</button>
            )}
            <input value={med.name} onChange={e => updateMed(i, 'name', e.target.value)} placeholder="Medicine name *"
              className="w-full p-2.5 rounded-lg border border-border mb-2 bg-surface text-sm" />
            <div className="grid grid-cols-2 gap-2">
              <input value={med.dosage} onChange={e => updateMed(i, 'dosage', e.target.value)} placeholder="Dosage"
                className="p-2 rounded-lg border border-border bg-surface text-sm" />
              <input value={med.frequency} onChange={e => updateMed(i, 'frequency', e.target.value)} placeholder="Frequency"
                className="p-2 rounded-lg border border-border bg-surface text-sm" />
              <input type="number" value={med.duration_days} onChange={e => updateMed(i, 'duration_days', parseInt(e.target.value))} placeholder="Days"
                className="p-2 rounded-lg border border-border bg-surface text-sm" />
              <input value={med.instructions} onChange={e => updateMed(i, 'instructions', e.target.value)} placeholder="Instructions"
                className="p-2 rounded-lg border border-border bg-surface text-sm" />
            </div>
          </div>
        ))}
        <button onClick={addMed} className="text-primary font-medium text-sm mb-4 min-h-[40px]">+ Add Medicine</button>

        <div className="mb-4">
          <label className="text-sm font-medium text-text-mid mb-1 block">Advice</label>
          <textarea value={advice} onChange={e => setAdvice(e.target.value)} rows={2}
            className="w-full p-3 rounded-xl border border-border bg-background text-sm" placeholder="Rest, drink fluids..." />
        </div>
        <div className="mb-4">
          <label className="text-sm font-medium text-text-mid mb-1 block">Follow-up Date</label>
          <input type="date" value={followUp} onChange={e => setFollowUp(e.target.value)}
            className="p-3 rounded-xl border border-border bg-background text-sm" />
        </div>

        {error && <p className="text-urgency-red text-sm mb-3">{error}</p>}
        <button onClick={handleSubmit} disabled={loading}
          className="w-full py-3 bg-primary text-white rounded-xl font-semibold disabled:opacity-50 min-h-[48px]">
          {loading ? 'Saving...' : 'Save Prescription'}
        </button>
      </div>
    </div>
  )
}
