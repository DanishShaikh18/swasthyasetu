import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import useAuthStore from './store/authStore'
import { checkNetwork, watchNetwork } from './utils/networkCheck'
import { useTranslation } from 'react-i18next'

import BottomNav from './components/BottomNav'
import LanguageSwitcher from './components/LanguageSwitcher'
import Home from './pages/Home'
import SymptomChecker from './pages/SymptomChecker'
import Doctors from './pages/Doctors'
import BookAppointment from './pages/BookAppointment'
import Prescriptions from './pages/Prescriptions'
import MedicineSearch from './pages/MedicineSearch'
import VideoCall from './pages/VideoCall'
import Profile from './pages/Profile'
import Login from './pages/Login'
import Register from './pages/Register'

function ProtectedRoute({ children }) {
  const isAuth = useAuthStore((s) => s.isAuthenticated)
  return isAuth ? children : <Navigate to="/login" />
}

export default function App() {
  const [isOnline, setIsOnline] = useState(true)
  const { t } = useTranslation()

  useEffect(() => {
    const { isOnline: online } = checkNetwork()
    setIsOnline(online)
    watchNetwork(setIsOnline)
  }, [])

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Offline banner */}
      {!isOnline && (
        <div className="bg-urgency-yellow text-white text-center py-2 px-4 text-sm font-medium sticky top-0 z-50">
          {t('home.offline')}
        </div>
      )}

      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
        <Route path="/symptoms" element={<ProtectedRoute><SymptomChecker /></ProtectedRoute>} />
        <Route path="/doctors" element={<ProtectedRoute><Doctors /></ProtectedRoute>} />
        <Route path="/book/:doctorId" element={<ProtectedRoute><BookAppointment /></ProtectedRoute>} />
        <Route path="/prescriptions" element={<ProtectedRoute><Prescriptions /></ProtectedRoute>} />
        <Route path="/medicine" element={<ProtectedRoute><MedicineSearch /></ProtectedRoute>} />
        <Route path="/video/:appointmentId" element={<ProtectedRoute><VideoCall /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>

      {useAuthStore.getState().isAuthenticated && <BottomNav />}
    </div>
  )
}
