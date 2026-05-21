import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from '../../api';
import Spinner from '../../components/Spinner';
import StatusBadge from '../../components/StatusBadge';
import EmptyState from '../../components/EmptyState';
import Modal from '../../components/Modal';

export default function PatientAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [videoModal, setVideoModal] = useState(null);
  const [joining, setJoining] = useState(false);
  const [searchParams] = useSearchParams();

  const loadAppointments = useCallback(async () => {
    setLoading(true);
    try {
      let url = '/patients/me/appointments?limit=50';
      if (statusFilter) url += `&status=${statusFilter}`;
      const res = await api.get(url);
      setAppointments(res.data?.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadAppointments();
  }, [loadAppointments]);

  // Auto-join if URL has ?join=id
  useEffect(() => {
    const joinId = searchParams.get('join');
    if (joinId && appointments.length > 0) {
      const appt = appointments.find((a) => a.id === joinId);
      if (appt) joinCall(appt.id);
    }
  }, [searchParams, appointments]);

  const joinCall = async (appointmentId) => {
    setJoining(true);
    try {
      const res = await api.get(`/appointments/${appointmentId}/join`);
      setVideoModal(res.data);
    } catch (err) {
      alert(err.message || 'Cannot join call');
    } finally {
      setJoining(false);
    }
  };

  const statuses = ['', 'confirmed', 'pending', 'completed', 'cancelled'];

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Appointments</h1>

      {/* Filter */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {statuses.map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap border transition-all ${
              statusFilter === s
                ? 'bg-primary-600 text-white border-primary-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-primary-300'
            }`}
          >
            {s ? s.charAt(0).toUpperCase() + s.slice(1) : 'All'}
          </button>
        ))}
      </div>

      {loading ? (
        <Spinner />
      ) : appointments.length === 0 ? (
        <EmptyState
          icon="📅"
          title="No appointments"
          description="You haven't booked any appointments yet."
        />
      ) : (
        <div className="space-y-3">
          {appointments.map((appt) => (
            <div key={appt.id} className="bg-white rounded-2xl border border-gray-100 p-5 hover:border-gray-200 transition-all">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900">{appt.doctor_name}</h3>
                    <StatusBadge status={appt.status} />
                  </div>
                  <p className="text-sm text-primary-600">{appt.doctor_specialization}</p>
                  <p className="text-sm text-gray-500 mt-1">
                    📅 {new Date(appt.scheduled_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
                  </p>
                  {appt.chief_complaint && (
                    <p className="text-sm text-gray-400 mt-1">💬 {appt.chief_complaint}</p>
                  )}
                </div>

                {appt.status === 'confirmed' && (
                  <button
                    onClick={() => joinCall(appt.id)}
                    disabled={joining}
                    className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50 shrink-0"
                  >
                    {joining ? 'Joining...' : '📹 Join Video Call'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Video Call Modal */}
      <Modal open={!!videoModal} onClose={() => setVideoModal(null)} title="Video Consultation" maxWidth="max-w-2xl">
        {videoModal && (
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-4">Your video room is ready!</p>
            <a
              href={videoModal.room_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-6 py-3 bg-emerald-600 text-white rounded-xl font-medium hover:bg-emerald-700 transition-colors"
            >
              Open Video Call →
            </a>
            <p className="text-xs text-gray-400 mt-3">
              Room: {videoModal.room_name}
            </p>
          </div>
        )}
      </Modal>
    </div>
  );
}
