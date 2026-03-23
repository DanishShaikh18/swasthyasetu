import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import useAuthStore from '../store/authStore'
import { getProfile, updateProfile } from '../api/patient'
import { logout as logoutApi } from '../api/auth'
import LanguageSwitcher from '../components/LanguageSwitcher'

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(true)
  const logout = useAuthStore(s => s.logout)
  const navigate = useNavigate()
  const { t } = useTranslation()

  useEffect(() => {
    getProfile().then(r => {
      setProfile(r.data?.data)
      setForm(r.data?.data || {})
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    try {
      await updateProfile(form)
      setProfile(form); setEditing(false)
    } catch {}
  }

  const handleLogout = async () => {
    try { await logoutApi() } catch {}
    logout(); navigate('/login')
  }

  if (loading) return <div className="p-4 space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-12 rounded-xl" />)}</div>

  const Field = ({ label, value, field }) => (
    <div className="flex justify-between items-center py-3 border-b border-border">
      <span className="text-sm text-text-mid">{label}</span>
      {editing ? (
        <input value={form[field] || ''} onChange={e => setForm(f => ({...f, [field]: e.target.value}))}
          className="text-right text-sm p-1 border border-border rounded-lg max-w-[180px]" />
      ) : (
        <span className="text-sm font-medium text-text-dark">{value || '—'}</span>
      )}
    </div>
  )

  return (
    <div className="px-4 py-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold text-text-dark">{t('profile.title')}</h1>
        <button onClick={() => editing ? handleSave() : setEditing(true)}
          className="px-4 py-2 rounded-xl text-sm font-medium min-h-[40px] bg-primary text-white">
          {editing ? t('profile.save') : t('profile.editProfile')}
        </button>
      </div>

      <LanguageSwitcher />

      <div className="bg-surface rounded-2xl p-4 border border-border mt-3">
        <h3 className="font-semibold text-text-mid text-sm mb-2">{t('profile.personalInfo')}</h3>
        <Field label={t('auth.name')} value={profile?.full_name} field="full_name" />
        <Field label={t('auth.email')} value={profile?.email} field="email" />
        <Field label={t('auth.phone')} value={profile?.phone} field="phone" />
        <Field label={t('profile.village')} value={profile?.village} field="village" />
        <Field label={t('profile.district')} value={profile?.district} field="district" />
        <Field label={t('profile.state')} value={profile?.state} field="state" />
      </div>

      <div className="bg-surface rounded-2xl p-4 border border-border mt-3">
        <h3 className="font-semibold text-text-mid text-sm mb-2">{t('profile.medicalInfo')}</h3>
        <Field label={t('profile.bloodGroup')} value={profile?.blood_group} field="blood_group" />
        <Field label={t('profile.allergies')} value={(profile?.allergies || []).join(', ')} field="allergies" />
        <Field label={t('profile.conditions')} value={(profile?.chronic_conditions || []).join(', ')} field="chronic_conditions" />
        <Field label={t('profile.emergencyContact')} value={profile?.emergency_contact_name} field="emergency_contact_name" />
      </div>

      <button onClick={handleLogout}
        className="w-full mt-6 py-3 bg-urgency-red text-white rounded-xl font-semibold min-h-[48px]">
        {t('profile.logout')}
      </button>
    </div>
  )
}
