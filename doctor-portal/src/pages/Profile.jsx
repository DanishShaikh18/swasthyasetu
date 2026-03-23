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

  if (loading) return <div className="p-6"><div className="h-40 bg-gray-100 rounded-2xl animate-pulse" /></div>

  const Field = ({ label, value, field }) => (
    <div className="flex justify-between items-center py-2.5 border-b border-border text-sm">
      <span className="text-text-muted">{label}</span>
      {editing ? <input value={form[field] || ''} onChange={e => setForm(f => ({...f, [field]: e.target.value}))} className="text-right p-1 border border-border rounded-lg max-w-[200px]" /> : <span className="font-medium">{value || '—'}</span>}
    </div>
  )

  return (
    <div className="p-6 max-w-2xl">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">My Profile</h1>
        <button onClick={() => editing ? handleSave() : setEditing(true)}
          className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium min-h-[40px]">
          {editing ? 'Save' : 'Edit'}
        </button>
      </div>

      <div className="bg-surface rounded-2xl p-5 border border-border">
        <Field label="Specialization" value={profile?.specialization} field="specialization" />
        <Field label="Qualification" value={profile?.qualification} field="qualification" />
        <Field label="Registration No." value={profile?.registration_number} field="registration_number" />
        <Field label="Experience" value={`${profile?.experience_years} years`} field="experience_years" />
        <Field label="Hospital" value={profile?.hospital_name} field="hospital_name" />
        <Field label="Consultation Fee" value={`₹${profile?.consultation_fee || 0}`} field="consultation_fee" />
        <Field label="Bio" value={profile?.bio} field="bio" />
        <Field label="Status" value={profile?.is_approved ? '✅ Approved' : '⏳ Pending Approval'} field="" />
      </div>

      <button onClick={handleLogout}
        className="w-full mt-6 py-3 bg-urgency-red text-white rounded-xl font-semibold min-h-[48px]">
        Logout
      </button>
    </div>
  )
}
