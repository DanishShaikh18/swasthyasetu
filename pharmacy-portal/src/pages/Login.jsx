import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login as loginApi } from '../api'
import useAuthStore from '../store/authStore'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore(s => s.setAuth)

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError('')
    try {
      const res = await loginApi({ email, password })
      if (res.data.data.role !== 'pharmacy') { setError('This portal is for pharmacies only'); return }
      setAuth(res.data.data); navigate('/')
    } catch { setError('Invalid credentials') }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6 bg-background">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary">💊 Pharmacy Portal</h1>
          <p className="text-text-mid mt-2">SwasthyaSetu — स्वास्थ्य सेतु</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-surface rounded-2xl p-6 shadow-sm border border-border">
          <h2 className="text-xl font-semibold mb-4">Pharmacy Login</h2>
          {error && <p className="text-danger text-sm mb-3 p-2 bg-red-50 rounded-lg">{error}</p>}
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="Email"
            className="w-full p-3 rounded-xl border border-border mb-3 bg-background" />
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="Password"
            className="w-full p-3 rounded-xl border border-border mb-4 bg-background" />
          <button type="submit" disabled={loading}
            className="w-full py-3 bg-primary text-white rounded-xl font-semibold disabled:opacity-50 min-h-[48px]">
            {loading ? '...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  )
}
