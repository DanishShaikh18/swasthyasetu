import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import useAuthStore from '../store/authStore'
import LanguageSwitcher from '../components/LanguageSwitcher'
import EmergencyPanel from '../components/EmergencyPanel'
import { getDailyTip } from '../api/ai'

export default function Home() {
  const user = useAuthStore(s => s.user)
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const [tip, setTip] = useState(null)

  useEffect(() => {
    getDailyTip({ language: i18n.language }).then(r => {
      if (r.data?.data) setTip(r.data.data)
    }).catch(() => {})
  }, [i18n.language])

  const actions = [
    { key: 'symptoms', icon: '🩺', path: '/symptoms' },
    { key: 'doctors', icon: '👨‍⚕️', path: '/doctors' },
    { key: 'medicine', icon: '💊', path: '/medicine' },
    { key: 'prescriptions', icon: '📋', path: '/prescriptions' },
  ]

  return (
    <div className="pb-4">
      <LanguageSwitcher />

      {/* Greeting */}
      <div className="px-4 py-3">
        <h1 className="text-2xl font-bold text-text-dark">
          {t('home.greeting')}, {user?.fullName || 'User'} जी
        </h1>
      </div>

      {/* Daily Health Tip */}
      {tip && (
        <div className="mx-4 mb-4 bg-surface rounded-2xl p-4 border-l-4 border-primary shadow-sm">
          <h3 className="text-sm font-semibold text-primary mb-1">🌿 {t('home.dailyTip')}</h3>
          <p className="text-sm text-text-dark leading-relaxed">{tip.title}</p>
          <p className="text-xs text-text-mid mt-1">{tip.body?.substring(0, 120)}...</p>
        </div>
      )}

      {/* 2×2 Action Grid */}
      <div className="grid grid-cols-2 gap-3 px-4 mb-4">
        {actions.map(a => (
          <button key={a.key} onClick={() => navigate(a.path)}
            className="bg-surface rounded-2xl p-5 border border-border shadow-sm hover:shadow-md hover:border-primary/30 active:scale-[0.97] transition-all min-h-[100px] flex flex-col items-center justify-center gap-2">
            <span className="text-3xl">{a.icon}</span>
            <span className="text-sm font-medium text-text-dark text-center">{t(`home.actionGrid.${a.key}`)}</span>
          </button>
        ))}
      </div>

      {/* Emergency SOS */}
      <EmergencyPanel />
    </div>
  )
}
