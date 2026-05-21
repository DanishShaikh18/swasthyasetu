import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../AuthContext';
import api from '../../api';
import Spinner from '../../components/Spinner';
import StatusBadge from '../../components/StatusBadge';

export default function PatientDashboard() {
  const { user } = useAuth();
  const [upcoming, setUpcoming] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [apptRes, profileRes] = await Promise.all([
          api.get('/patients/me/appointments?status=confirmed&limit=5'),
          api.get('/patients/me'),
        ]);
        setUpcoming(apptRes.data?.items || []);
        setProfile(profileRes.data);
      } catch (err) {
        console.error('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Spinner />;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {user.full_name} 👋
        </h1>
        <p className="text-gray-500 mt-1">Here's your health overview</p>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <Link to="/patient/doctors" className="group p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">🔍</div>
          <p className="font-medium text-sm text-gray-900 group-hover:text-primary-700">Find Doctors</p>
          <p className="text-xs text-gray-400 mt-0.5">Book consultation</p>
        </Link>
        <Link to="/patient/appointments" className="group p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">📅</div>
          <p className="font-medium text-sm text-gray-900 group-hover:text-primary-700">Appointments</p>
          <p className="text-xs text-gray-400 mt-0.5">View schedule</p>
        </Link>
        <Link to="/patient/prescriptions" className="group p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">💊</div>
          <p className="font-medium text-sm text-gray-900 group-hover:text-primary-700">Prescriptions</p>
          <p className="text-xs text-gray-400 mt-0.5">Your medicines</p>
        </Link>
        <Link to="/patient/profile" className="group p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">👤</div>
          <p className="font-medium text-sm text-gray-900 group-hover:text-primary-700">Profile</p>
          <p className="text-xs text-gray-400 mt-0.5">Update details</p>
        </Link>
      </div>

      {/* Upcoming appointments */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Upcoming Appointments</h2>
          <Link to="/patient/appointments" className="text-sm text-primary-600 hover:underline font-medium">
            View All →
          </Link>
        </div>

        {upcoming.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-400 text-sm">No upcoming appointments</p>
            <Link to="/patient/doctors" className="mt-3 inline-block text-sm text-primary-600 hover:underline font-medium">
              Book your first appointment →
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {upcoming.map((appt) => (
              <div key={appt.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                <div>
                  <p className="font-medium text-gray-900">{appt.doctor_name}</p>
                  <p className="text-sm text-gray-500">{appt.doctor_specialization}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(appt.scheduled_at).toLocaleString('en-IN', {
                      dateStyle: 'medium',
                      timeStyle: 'short',
                    })}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={appt.status} />
                  {appt.status === 'confirmed' && (
                    <Link
                      to={`/patient/appointments?join=${appt.id}`}
                      className="px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700 transition-colors"
                    >
                      Join Call
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
