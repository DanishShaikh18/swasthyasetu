import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { login as loginApi } from '../api/auth'
import useAuthStore from '../store/authStore'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const { t } = useTranslation()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      const res = await loginApi({ email, password })
      setAuth(res.data.data)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail?.error?.message || 'Login failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 bg-background">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary">🏥 SwasthyaSetu</h1>
          <p className="text-text-mid mt-2">स्वास्थ्य सेतु — Health Bridge</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-surface rounded-2xl p-6 shadow-sm border border-border">
          <h2 className="text-xl font-semibold text-text-dark mb-4">{t('auth.login')}</h2>
          {error && <p className="text-urgency-red text-sm mb-3 p-2 bg-red-50 rounded-lg">{error}</p>}
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
            placeholder={t('auth.email')}
            className="w-full p-3 rounded-xl border border-border mb-3 bg-background text-base min-h-[48px]" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
            placeholder={t('auth.password')}
            className="w-full p-3 rounded-xl border border-border mb-4 bg-background text-base min-h-[48px]" />
          <button type="submit" disabled={loading}
            className="w-full py-3 bg-primary text-white rounded-xl font-semibold text-base hover:bg-primary-dark disabled:opacity-50 min-h-[48px] transition-all">
            {loading ? '...' : t('auth.loginBtn')}
          </button>
          <p className="text-center text-sm text-text-mid mt-4">
            {t('auth.noAccount')} <Link to="/register" className="text-primary font-medium">{t('auth.register')}</Link>
          </p>
        </form>
      </div>
    </div>
  )
}
