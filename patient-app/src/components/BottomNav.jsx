import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function BottomNav() {
  const { t } = useTranslation()
  const navItems = [
    { to: '/', icon: '🏠', label: t('nav.home') },
    { to: '/doctors', icon: '👨‍⚕️', label: t('nav.doctors') },
    { to: '/prescriptions', icon: '📋', label: t('nav.records') },
    { to: '/profile', icon: '👤', label: t('nav.profile') },
  ]

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-surface border-t border-border z-50">
      <div className="flex justify-around items-center max-w-lg mx-auto">
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === '/'}
            className={({ isActive }) =>
              `flex flex-col items-center py-2 px-3 min-w-[64px] min-h-[48px] transition-colors ${
                isActive ? 'text-primary font-semibold' : 'text-text-muted'
              }`
            }>
            <span className="text-xl">{item.icon}</span>
            <span className="text-xs mt-0.5">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
