import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { useState } from 'react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!user) return null;

  const isDoctor = user.role === 'doctor';
  const prefix = isDoctor ? '/doctor' : '/patient';

  const links = isDoctor
    ? [
        { to: '/doctor/dashboard', label: 'Dashboard' },
        { to: '/doctor/appointments', label: 'Appointments' },
        { to: '/doctor/slots', label: 'Slots' },
        { to: '/doctor/profile', label: 'Profile' },
        { to: '/doctor/notifications', label: 'Notifications' },
      ]
    : [
        { to: '/patient/dashboard', label: 'Dashboard' },
        { to: '/patient/doctors', label: 'Find Doctors' },
        { to: '/patient/appointments', label: 'Appointments' },
        { to: '/patient/prescriptions', label: 'Prescriptions' },
        { to: '/patient/profile', label: 'Profile' },
        { to: '/patient/notifications', label: 'Notifications' },
      ];

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to={`${prefix}/dashboard`} className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <span className="text-white font-bold text-sm">SS</span>
            </div>
            <span className="font-bold text-lg text-gray-900">SwasthyaSetu</span>
            <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full font-medium">
              {isDoctor ? 'Doctor' : 'Patient'}
            </span>
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-1">
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  location.pathname === l.to
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {l.label}
              </Link>
            ))}
          </div>

          {/* User menu */}
          <div className="flex items-center gap-3">
            <span className="hidden sm:block text-sm text-gray-600">
              {user.full_name}
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-500 hover:text-rose-600 font-medium transition-colors"
            >
              Logout
            </button>
            {/* Mobile menu toggle */}
            <button
              className="md:hidden p-2 text-gray-500"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {menuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden pb-3 border-t border-gray-100 animate-fade-in">
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                onClick={() => setMenuOpen(false)}
                className={`block px-3 py-2 rounded-lg text-sm font-medium mt-1 ${
                  location.pathname === l.to
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                {l.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
