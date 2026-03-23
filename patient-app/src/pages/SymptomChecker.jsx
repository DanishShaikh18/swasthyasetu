import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import VoiceInput from '../components/VoiceInput'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { checkSymptoms } from '../api/ai'

export default function SymptomChecker() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()

  const urgencyColors = { green: 'bg-urgency-green', yellow: 'bg-urgency-yellow', red: 'bg-urgency-red' }

  const handleSubmit = async () => {
    if (!text.trim()) return
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await checkSymptoms({ symptoms: text, language: i18n.language })
      setResult(res.data.data)
    } catch (err) {
      if (err.response?.status === 429) {
        setError(t('symptoms.rateLimit'))
      } else {
        setError(err.response?.data?.detail?.error?.message || t('common.error'))
      }
    } finally { setLoading(false) }
  }

  return (
    <div className="px-4 py-4">
      <h1 className="text-xl font-bold text-text-dark mb-3">{t('symptoms.title')}</h1>
      <LanguageSwitcher />

      {/* Voice Input — prominently placed */}
      <div className="my-4">
        <VoiceInput language={i18n.language} onResult={(transcript) => setText(prev => prev ? prev + ' ' + transcript : transcript)} />
      </div>

      {/* Text Input */}
      <textarea value={text} onChange={e => setText(e.target.value)}
        placeholder={t('symptoms.placeholder')} rows={4}
        className="w-full p-4 rounded-xl border border-border bg-surface text-base resize-none focus:outline-none focus:border-primary" />

      <button onClick={handleSubmit} disabled={loading || !text.trim()}
        className="w-full mt-3 py-3 bg-primary text-white rounded-xl font-semibold disabled:opacity-50 min-h-[48px] transition-all">
        {loading ? t('common.loading') : t('symptoms.submit')}
      </button>

      {error && <p className="text-urgency-red text-sm mt-3 p-3 bg-red-50 rounded-xl">{error}</p>}

      {/* Result Card */}
      {result && (
        <div className="mt-4 bg-surface rounded-2xl border border-border p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <span className={`px-3 py-1 rounded-full text-white text-sm font-medium ${urgencyColors[result.urgency_color] || 'bg-urgency-yellow'}`}>
              {result.urgency === 'high' ? '🔴' : result.urgency === 'medium' ? '🟡' : '🟢'} {result.urgency?.toUpperCase()}
            </span>
          </div>
          <h3 className="font-semibold text-text-dark text-lg mb-2">{result.possible_condition}</h3>
          <p className="text-sm text-text-dark leading-relaxed mb-3">{result.advice}</p>

          {result.call_emergency && (
            <a href="tel:102" className="block w-full py-3 bg-emergency text-white rounded-xl text-center font-bold mb-3 min-h-[48px] flex items-center justify-center">
              🚨 Call 102 — Emergency
            </a>
          )}

          {result.see_doctor_now && (
            <button onClick={() => navigate('/doctors')} className="w-full py-3 bg-primary text-white rounded-xl font-medium min-h-[48px]">
              {t('symptoms.bookDoctor')}
            </button>
          )}

          <p className="text-xs text-text-muted mt-3 italic">{result.disclaimer}</p>
        </div>
      )}
    </div>
  )
}
