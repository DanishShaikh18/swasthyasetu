import { useState, useEffect } from 'react'
import { getSlots, createSlotTemplate } from '../api'

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

export default function Slots() {
  const [slots, setSlots] = useState([])
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({ day_of_week: 0, start_time: '09:00', end_time: '17:00', slot_duration_min: 15 })
  const [saving, setSaving] = useState(false)

  useEffect(() => { fetchSlots() }, [])

  const fetchSlots = async () => {
    setLoading(true)
    try { const r = await getSlots(); setSlots(r.data?.data || []) } catch {} finally { setLoading(false) }
  }

  const handleCreate = async () => {
    setSaving(true)
    try { await createSlotTemplate(form); fetchSlots() } catch {} finally { setSaving(false) }
  }

  const grouped = DAYS.map((day, i) => ({
    day, slots: slots.filter(s => s.day_of_week === i)
  }))

  return (
    <div className="p-6 max-w-3xl">
      <h1 className="text-2xl font-bold mb-4">Schedule Management</h1>

      {/* Add Slot Template */}
      <div className="bg-surface rounded-2xl p-5 border border-border mb-6">
        <h3 className="font-semibold mb-3">Add Slot Template</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <select value={form.day_of_week} onChange={e => setForm(f => ({...f, day_of_week: parseInt(e.target.value)}))}
            className="p-2.5 rounded-xl border border-border bg-background text-sm">
            {DAYS.map((d, i) => <option key={i} value={i}>{d}</option>)}
          </select>
          <input type="time" value={form.start_time} onChange={e => setForm(f => ({...f, start_time: e.target.value}))}
            className="p-2.5 rounded-xl border border-border bg-background text-sm" />
          <input type="time" value={form.end_time} onChange={e => setForm(f => ({...f, end_time: e.target.value}))}
            className="p-2.5 rounded-xl border border-border bg-background text-sm" />
          <select value={form.slot_duration_min} onChange={e => setForm(f => ({...f, slot_duration_min: parseInt(e.target.value)}))}
            className="p-2.5 rounded-xl border border-border bg-background text-sm">
            <option value={10}>10 min</option><option value={15}>15 min</option>
            <option value={20}>20 min</option><option value={30}>30 min</option>
          </select>
        </div>
        <button onClick={handleCreate} disabled={saving}
          className="mt-3 px-6 py-2.5 bg-primary text-white rounded-xl font-medium text-sm disabled:opacity-50 min-h-[40px]">
          {saving ? 'Adding...' : 'Add Template'}
        </button>
      </div>

      {/* Weekly View */}
      <h2 className="text-lg font-semibold mb-3">Weekly Schedule</h2>
      {loading ? (
        <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-16 bg-gray-100 rounded-xl animate-pulse" />)}</div>
      ) : (
        <div className="space-y-3">
          {grouped.map(g => (
            <div key={g.day} className="bg-surface rounded-xl p-4 border border-border">
              <h4 className="font-medium text-sm text-text-mid mb-2">{g.day}</h4>
              {g.slots.length === 0 ? (
                <p className="text-xs text-text-muted">No slots configured</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {g.slots.map(s => (
                    <span key={s.id} className="text-xs bg-primary-light text-primary px-3 py-1.5 rounded-full font-medium">
                      {s.start_time} — {s.end_time} ({s.slot_duration_min}min)
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
