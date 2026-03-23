import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { register as registerApi } from '../api/auth'
import useAuthStore from '../store/authStore'

export default function Register() {
  const [form, setForm] = useState({ email:'', phone:'', password:'', full_name:'', role:'patient', preferred_language:'hi' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore(s => s.setAuth)
  const { t } = useTranslation()

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError('')
    try {
      const res = await registerApi(form)
      setAuth(res.data.data)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail?.error?.message || 'Registration failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 bg-background">
      <div className="w-full max-w-sm">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-primary">🏥 SwasthyaSetu</h1>
        </div>
        <form onSubmit={handleSubmit} className="bg-surface rounded-2xl p-6 shadow-sm border border-border">
          <h2 className="text-xl font-semibold text-text-dark mb-4">{t('auth.register')}</h2>
          {error && <p className="text-urgency-red text-sm mb-3 p-2 bg-red-50 rounded-lg">{error}</p>}
          <input value={form.full_name} onChange={e => update('full_name', e.target.value)} required
            placeholder={t('auth.name')} className="w-full p-3 rounded-xl border border-border mb-3 bg-background min-h-[48px]" />
          <input type="email" value={form.email} onChange={e => update('email', e.target.value)} required
            placeholder={t('auth.email')} className="w-full p-3 rounded-xl border border-border mb-3 bg-background min-h-[48px]" />
          <input value={form.phone} onChange={e => update('phone', e.target.value)} required
            placeholder={t('auth.phone')} className="w-full p-3 rounded-xl border border-border mb-3 bg-background min-h-[48px]" />
          <input type="password" value={form.password} onChange={e => update('password', e.target.value)} required minLength={6}
            placeholder={t('auth.password')} className="w-full p-3 rounded-xl border border-border mb-4 bg-background min-h-[48px]" />
          <button type="submit" disabled={loading}
            className="w-full py-3 bg-primary text-white rounded-xl font-semibold disabled:opacity-50 min-h-[48px]">
            {loading ? '...' : t('auth.registerBtn')}
          </button>
          <p className="text-center text-sm text-text-mid mt-4">
            {t('auth.hasAccount')} <Link to="/login" className="text-primary font-medium">{t('auth.login')}</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
