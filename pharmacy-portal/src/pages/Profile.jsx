import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { getProfile, updateProfile, logout as logoutApi } from '../api'

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(true)
  const logoutState = useAuthStore(s => s.logout)
  const navigate = useNavigate()

  useEffect(() => {
    getProfile().then(r => { setProfile(r.data?.data); setForm(r.data?.data || {}) }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    try { await updateProfile(form); setProfile(form); setEditing(false) } catch {}
  }

  const handleLogout = async () => {
    try { await logoutApi() } catch {}
    logoutState(); navigate('/login')
  }

  if (loading) return <div className="p-6"><div className="h-40 bg-amber-50 rounded-2xl animate-pulse" /></div>

  const Field = ({ label, value, field }) => (
    <div className="flex justify-between items-center py-2.5 border-b border-border text-sm">
      <span className="text-text-muted">{label}</span>
      {editing && field ? <input value={form[field] || ''} onChange={e => setForm(f => ({...f, [field]: e.target.value}))} className="text-right p-1 border border-border rounded-lg max-w-[200px]" /> : <span className="font-medium">{value || '—'}</span>}
    </div>
  )

  return (
    <div className="p-6 max-w-2xl">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Pharmacy Profile</h1>
        <button onClick={() => editing ? handleSave() : setEditing(true)}
          className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium min-h-[40px]">
          {editing ? 'Save' : 'Edit'}
        </button>
      </div>

      <div className="bg-surface rounded-2xl p-5 border border-border">
        <Field label="Pharmacy Name" value={profile?.pharmacy_name} field="pharmacy_name" />
        <Field label="License Number" value={profile?.license_number} field="license_number" />
        <Field label="Address" value={profile?.address} field="address" />
        <Field label="Village" value={profile?.village} field="village" />
        <Field label="District" value={profile?.district} field="district" />
        <Field label="State" value={profile?.state} field="state" />
        <Field label="Phone" value={profile?.phone} field="phone" />
        <Field label="Status" value={profile?.is_approved ? '✅ Approved' : '⏳ Pending'} field="" />
        <Field label="Currently Open" value={profile?.is_open_now ? '🟢 Open' : '🔴 Closed'} field="" />
      </div>

      {profile?.opening_hours && (
        <div className="bg-surface rounded-2xl p-5 border border-border mt-4">
          <h3 className="font-semibold text-sm text-text-mid mb-3">Opening Hours</h3>
          {Object.entries(profile.opening_hours).map(([k, v]) => (
            <div key={k} className="flex justify-between py-1.5 text-sm">
              <span className="text-text-muted capitalize">{k.replace('_', '-')}</span>
              <span className="font-medium">{v}</span>
            </div>
          ))}
        </div>
      )}

      <button onClick={handleLogout}
        className="w-full mt-6 py-3 bg-danger text-white rounded-xl font-semibold min-h-[48px]">
        Logout
      </button>
    </div>
  )
}
