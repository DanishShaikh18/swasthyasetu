import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login as loginApi, register as registerApi } from '../api'
import useAuthStore from '../store/authStore'

export default function Login() {
  const [tab, setTab] = useState('login')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore(s => s.setAuth)

  // Login state
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')

  // Register state
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [pharmacyName, setPharmacyName] = useState('')

  const handleLogin = async (e) => {
    e.preventDefault(); setLoading(true); setError('')
    try {
      const res = await loginApi({ email: loginEmail, password: loginPassword })
      if (res.data.data.role !== 'pharmacy') { setError('This portal is for pharmacies only'); return }
      setAuth(res.data.data); navigate('/')
    } catch (err) {
      const msg = err.response?.data?.detail?.message || 'Invalid credentials'
      setError(msg)
    }
    finally { setLoading(false) }
  }

  const handleRegister = async (e) => {
    e.preventDefault(); setLoading(true); setError('')
    if (password.length < 8) { setError('Password must be at least 8 characters'); setLoading(false); return }
    if (phone.length !== 10) { setError('Phone must be 10 digits'); setLoading(false); return }
    try {
      const res = await registerApi({
        full_name: fullName,
        email,
        phone: `+91${phone}`,
        password,
        role: 'pharmacy',
        pharmacy_name: pharmacyName,
        address: 'To be updated',
      })
      setAuth(res.data.data); navigate('/')
    } catch (err) {
      const msg = err.response?.data?.detail?.message || 'Registration failed'
      setError(msg)
    }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6 bg-background">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary">💊 Pharmacy Portal</h1>
          <p className="text-text-mid mt-2">SwasthyaSetu — स्वास्थ्य सेतु</p>
        </div>

        {/* Tabs */}
        <div className="flex mb-4 bg-surface rounded-xl border border-border overflow-hidden">
          <button onClick={() => { setTab('login'); setError('') }}
            className={`flex-1 py-3 text-sm font-semibold transition-colors ${tab === 'login' ? 'bg-primary text-white' : 'text-text-mid hover:bg-gray-50'}`}>
            Login
          </button>
          <button onClick={() => { setTab('register'); setError('') }}
            className={`flex-1 py-3 text-sm font-semibold transition-colors ${tab === 'register' ? 'bg-primary text-white' : 'text-text-mid hover:bg-gray-50'}`}>
            Register
          </button>
        </div>

        {error && <p className="text-danger text-sm mb-3 p-2 bg-red-50 rounded-lg">{error}</p>}

        {tab === 'login' ? (
          <form onSubmit={handleLogin} className="bg-surface rounded-2xl p-6 shadow-sm border border-border">
            <h2 className="text-xl font-semibold mb-4">Pharmacy Login</h2>
            <input type="email" value={loginEmail} onChange={e => setLoginEmail(e.target.value)} required placeholder="Email"
              className="w-full p-3 rounded-xl border border-border mb-3 bg-background" />
            <input type="password" value={loginPassword} onChange={e => setLoginPassword(e.target.value)} required placeholder="Password"
              className="w-full p-3 rounded-xl border border-border mb-4 bg-background" />
            <button type="submit" disabled={loading}
              className="w-full py-3 bg-primary text-white rounded-xl font-semibold disabled:opacity-50 min-h-[48px]">
              {loading ? '...' : 'Login'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="bg-surface rounded-2xl p-6 shadow-sm border border-border">
            <h2 className="text-xl font-semibold mb-4">Pharmacy Registration</h2>
            <input type="text" value={fullName} onChange={e => setFullName(e.target.value)} required placeholder="Full Name (Owner)"
              className="w-full p-3 rounded-xl border border-border mb-3 bg-background" />
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="Email"
              className="w-full p-3 rounded-xl border border-border mb-3 bg-background" />
            <div className="flex mb-3">
              <span className="p-3 bg-gray-100 rounded-l-xl border border-r-0 border-border text-sm text-text-mid flex items-center">+91</span>
              <input type="tel" value={phone} onChange={e => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))} required
                placeholder="10-digit Phone" pattern="[0-9]{10}" title="Enter 10-digit phone number"
                className="flex-1 p-3 rounded-r-xl border border-border bg-background" />
            </div>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="Password (min 8 chars)"
              minLength={8} className="w-full p-3 rounded-xl border border-border mb-3 bg-background" />
            <input type="text" value={pharmacyName} onChange={e => setPharmacyName(e.target.value)} required placeholder="Pharmacy Name"
              className="w-full p-3 rounded-xl border border-border mb-4 bg-background" />
            <button type="submit" disabled={loading}
              className="w-full py-3 bg-primary text-white rounded-xl font-semibold disabled:opacity-50 min-h-[48px]">
              {loading ? '...' : 'Register Pharmacy'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
