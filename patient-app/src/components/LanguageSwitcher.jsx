import { useTranslation } from 'react-i18next'

const languages = [
  { code: 'hi', label: 'हिं' }, { code: 'en', label: 'EN' },
  { code: 'ta', label: 'தமிழ்' }, { code: 'te', label: 'తె' },
  { code: 'mr', label: 'मर' }, { code: 'gu', label: 'ગુ' },
  { code: 'kn', label: 'ಕ' }, { code: 'ml', label: 'മ' },
  { code: 'pa', label: 'ਪੰ' }, { code: 'or', label: 'ଓ' },
]

export default function LanguageSwitcher() {
  const { i18n } = useTranslation()

  return (
    <div className="flex flex-wrap gap-1.5 px-4 py-2">
      {languages.map((lang) => (
        <button key={lang.code}
          onClick={() => i18n.changeLanguage(lang.code)}
          className={`px-3 py-1.5 rounded-full text-sm font-medium min-h-[36px] min-w-[36px] transition-all ${
            i18n.language === lang.code
              ? 'bg-primary text-white shadow-sm'
              : 'bg-surface text-text-mid border border-border hover:bg-primary-light'
          }`}>
          {lang.label}
        </button>
      ))}
    </div>
  )
}
