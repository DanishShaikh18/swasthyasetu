import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import Navbar from './components/Navbar';
import { PageLoader } from './components/Spinner';

// Auth pages
import Login from './pages/Login';
import Register from './pages/Register';

// Patient pages
import PatientDashboard from './pages/patient/Dashboard';
import DoctorList from './pages/patient/DoctorList';
import DoctorProfile from './pages/patient/DoctorProfile';
import PatientAppointments from './pages/patient/Appointments';
import Prescriptions from './pages/patient/Prescriptions';
import PatientProfile from './pages/patient/Profile';

// Doctor pages
import DoctorDashboard from './pages/doctor/Dashboard';
import DoctorAppointments from './pages/doctor/Appointments';
import DoctorSlots from './pages/doctor/Slots';
import PatientRecord from './pages/doctor/PatientRecord';
import DoctorProfilePage from './pages/doctor/Profile';

// Shared
import Notifications from './pages/Notifications';

/** Protect routes by auth + role */
function ProtectedRoute({ children, role }) {
  const { user, loading } = useAuth();
  if (loading) return <PageLoader />;
  if (!user) return <Navigate to="/login" replace />;
  if (role && user.role !== role) return <Navigate to={`/${user.role}/dashboard`} replace />;
  return children;
}

export default function App() {
  const { user, loading } = useAuth();
  const isDoctorPort = window.location.port === '5174';

  if (loading) return <PageLoader />;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <Routes>
        {/* Public */}
        <Route path="/login" element={user ? <Navigate to={`/${user.role}/dashboard`} replace /> : <Login />} />
        <Route path="/register" element={user ? <Navigate to={`/${user.role}/dashboard`} replace /> : <Register />} />

        {/* Patient routes (only accessible on non-doctor port) */}
        {!isDoctorPort && (
          <>
            <Route path="/patient/dashboard" element={<ProtectedRoute role="patient"><PatientDashboard /></ProtectedRoute>} />
            <Route path="/patient/doctors" element={<ProtectedRoute role="patient"><DoctorList /></ProtectedRoute>} />
            <Route path="/patient/doctors/:doctorId" element={<ProtectedRoute role="patient"><DoctorProfile /></ProtectedRoute>} />
            <Route path="/patient/appointments" element={<ProtectedRoute role="patient"><PatientAppointments /></ProtectedRoute>} />
            <Route path="/patient/prescriptions" element={<ProtectedRoute role="patient"><Prescriptions /></ProtectedRoute>} />
            <Route path="/patient/profile" element={<ProtectedRoute role="patient"><PatientProfile /></ProtectedRoute>} />
            <Route path="/patient/notifications" element={<ProtectedRoute role="patient"><Notifications /></ProtectedRoute>} />
          </>
        )}

        {/* Doctor routes (only accessible on doctor port) */}
        {isDoctorPort && (
          <>
            <Route path="/doctor/dashboard" element={<ProtectedRoute role="doctor"><DoctorDashboard /></ProtectedRoute>} />
            <Route path="/doctor/appointments" element={<ProtectedRoute role="doctor"><DoctorAppointments /></ProtectedRoute>} />
            <Route path="/doctor/slots" element={<ProtectedRoute role="doctor"><DoctorSlots /></ProtectedRoute>} />
            <Route path="/doctor/patient/:patientId" element={<ProtectedRoute role="doctor"><PatientRecord /></ProtectedRoute>} />
            <Route path="/doctor/profile" element={<ProtectedRoute role="doctor"><DoctorProfilePage /></ProtectedRoute>} />
            <Route path="/doctor/notifications" element={<ProtectedRoute role="doctor"><Notifications /></ProtectedRoute>} />
          </>
        )}

        {/* Default */}
        <Route path="/" element={<Navigate to={user ? `/${user.role}/dashboard` : '/login'} replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
