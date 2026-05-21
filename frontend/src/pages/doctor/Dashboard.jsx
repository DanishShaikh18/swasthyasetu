import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../AuthContext';
import api from '../../api';
import Spinner from '../../components/Spinner';
import StatusBadge from '../../components/StatusBadge';

export default function DoctorDashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState({ pending: 0, confirmed: 0, completed: 0 });
  const [todayAppts, setTodayAppts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [profileRes, pendingRes, confirmedRes, completedRes] = await Promise.all([
          api.get('/doctors/me/profile'),
          api.get('/doctors/me/appointments?status=pending&limit=5'),
          api.get('/doctors/me/appointments?status=confirmed&limit=10'),
          api.get('/doctors/me/appointments?status=completed&limit=1'),
        ]);
        setProfile(profileRes.data);
        const pendingItems = pendingRes.data?.items || [];
        const confirmedItems = confirmedRes.data?.items || [];
        const completedItems = completedRes.data?.items || [];
        setStats({
          pending: pendingItems.length,
          confirmed: confirmedItems.length,
          completed: completedItems.length,
        });
        // Show upcoming confirmed as "today's" appointments
        setTodayAppts(confirmedItems.slice(0, 5));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Spinner />;

  const notApproved = profile && !profile.is_approved;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, Dr. {user.full_name} 👨‍⚕️
        </h1>
        <p className="text-gray-500 mt-1">
          {profile?.specialization} • {profile?.hospital_name || 'Independent Practice'}
        </p>
      </div>

      {notApproved && (
        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-2xl">
          <p className="text-amber-800 text-sm font-medium">⏳ Your account is pending admin approval. Some features may be limited.</p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <p className="text-2xl font-bold text-amber-600">{stats.pending}</p>
          <p className="text-sm text-gray-500 mt-1">Pending</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <p className="text-2xl font-bold text-primary-600">{stats.confirmed}</p>
          <p className="text-sm text-gray-500 mt-1">Confirmed</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <p className="text-2xl font-bold text-emerald-600">{stats.completed}</p>
          <p className="text-sm text-gray-500 mt-1">Completed</p>
        </div>
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <p className="text-2xl font-bold text-gray-600">{profile?.is_available ? '🟢' : '🔴'}</p>
          <p className="text-sm text-gray-500 mt-1">{profile?.is_available ? 'Available' : 'Unavailable'}</p>
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <Link to="/doctor/appointments" className="group p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">📋</div>
          <p className="font-medium text-sm text-gray-900 group-hover:text-primary-700">Appointments</p>
        </Link>
        <Link to="/doctor/slots" className="group p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">🕐</div>
          <p className="font-medium text-sm text-gray-900 group-hover:text-primary-700">Manage Slots</p>
        </Link>
        <Link to="/doctor/profile" className="group p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">👤</div>
          <p className="font-medium text-sm text-gray-900 group-hover:text-primary-700">Profile</p>
        </Link>
        <Link to="/doctor/notifications" className="group p-4 bg-white rounded-2xl border border-gray-100 hover:border-primary-200 hover:shadow-md transition-all">
          <div className="text-2xl mb-2">🔔</div>
          <p className="font-medium text-sm text-gray-900 group-hover:text-primary-700">Notifications</p>
        </Link>
      </div>

      {/* Upcoming */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Upcoming Appointments</h2>
          <Link to="/doctor/appointments" className="text-sm text-primary-600 hover:underline font-medium">View All →</Link>
        </div>
        {todayAppts.length === 0 ? (
          <p className="text-center py-8 text-gray-400 text-sm">No upcoming appointments</p>
        ) : (
          <div className="space-y-3">
            {todayAppts.map((appt) => (
              <div key={appt.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                <div>
                  <p className="font-medium text-gray-900">{appt.patient_name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {new Date(appt.scheduled_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
                    {appt.chief_complaint && ` • ${appt.chief_complaint}`}
                  </p>
                </div>
                <StatusBadge status={appt.status} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
