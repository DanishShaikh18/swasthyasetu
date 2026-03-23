import { useTranslation } from 'react-i18next'

export default function EmergencyPanel() {
  const { t } = useTranslation()
  return (
    <a href="tel:102" className="block">
      <div className="bg-emergency rounded-2xl p-5 text-white shadow-lg mx-4 mb-4 active:scale-[0.98] transition-transform">
        <div className="flex items-center gap-3">
          <span className="text-3xl">🚨</span>
          <div>
            <h3 className="font-bold text-lg">{t('home.emergency')}</h3>
            <p className="text-sm opacity-90 mt-0.5">{t('home.emergencyCall')}</p>
          </div>
        </div>
      </div>
    </a>
  )
}
