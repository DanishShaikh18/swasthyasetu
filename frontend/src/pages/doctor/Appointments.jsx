import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api';
import Spinner from '../../components/Spinner';
import StatusBadge from '../../components/StatusBadge';
import EmptyState from '../../components/EmptyState';
import Modal from '../../components/Modal';

export default function DoctorAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [actionLoading, setActionLoading] = useState(null);
  const [videoModal, setVideoModal] = useState(null);
  const [prescriptionModal, setPrescriptionModal] = useState(null);
  const [rxForm, setRxForm] = useState({
    diagnosis: '',
    advice: '',
    follow_up_date: '',
    medicines: [{ name: '', dosage: '', frequency: '', duration_days: '', instructions: '' }],
  });
  const [rxSaving, setRxSaving] = useState(false);

  const loadAppointments = useCallback(async () => {
    setLoading(true);
    try {
      let url = '/doctors/me/appointments?limit=50';
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

  const updateStatus = async (id, status) => {
    setActionLoading(id);
    try {
      await api.patch(`/doctors/me/appointments/${id}`, { status });
      await loadAppointments();
    } catch (err) {
      alert(err.message || 'Update failed');
    } finally {
      setActionLoading(null);
    }
  };

  const joinCall = async (appointmentId) => {
    try {
      const res = await api.get(`/appointments/${appointmentId}/join`);
      setVideoModal(res.data);
    } catch (err) {
      alert(err.message || 'Cannot join call');
    }
  };

  const addMedicine = () => {
    setRxForm({
      ...rxForm,
      medicines: [...rxForm.medicines, { name: '', dosage: '', frequency: '', duration_days: '', instructions: '' }],
    });
  };

  const removeMedicine = (index) => {
    setRxForm({
      ...rxForm,
      medicines: rxForm.medicines.filter((_, i) => i !== index),
    });
  };

  const updateMedicine = (index, field, value) => {
    const meds = [...rxForm.medicines];
    meds[index][field] = value;
    setRxForm({ ...rxForm, medicines: meds });
  };

  const submitPrescription = async () => {
    if (!prescriptionModal) return;
    setRxSaving(true);
    try {
      const payload = {
        appointment_id: prescriptionModal.id,
        patient_id: prescriptionModal.patient_id,
        diagnosis: rxForm.diagnosis || null,
        medicines: rxForm.medicines
          .filter((m) => m.name.trim())
          .map((m) => ({
            name: m.name,
            dosage: m.dosage || null,
            frequency: m.frequency || null,
            duration_days: m.duration_days ? parseInt(m.duration_days) : null,
            instructions: m.instructions || null,
          })),
        advice: rxForm.advice || null,
        follow_up_date: rxForm.follow_up_date || null,
      };
      if (payload.medicines.length === 0) {
        alert('Add at least one medicine');
        setRxSaving(false);
        return;
      }
      await api.post('/doctors/me/prescriptions', payload);
      alert('Prescription created!');
      setPrescriptionModal(null);
      setRxForm({
        diagnosis: '', advice: '', follow_up_date: '',
        medicines: [{ name: '', dosage: '', frequency: '', duration_days: '', instructions: '' }],
      });
    } catch (err) {
      alert(err.message || 'Failed to create prescription');
    } finally {
      setRxSaving(false);
    }
  };

  const statuses = ['', 'confirmed', 'pending', 'completed', 'cancelled'];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Appointments</h1>

      {/* Filter tabs */}
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
        <EmptyState icon="📋" title="No appointments" description="No appointments match your filter." />
      ) : (
        <div className="space-y-3">
          {appointments.map((appt) => (
            <div key={appt.id} className="bg-white rounded-2xl border border-gray-100 p-5">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <h3 className="font-semibold text-gray-900">{appt.patient_name}</h3>
                    <StatusBadge status={appt.status} />
                    {appt.type && (
                      <span className="text-xs text-gray-400">({appt.type})</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">
                    📅 {new Date(appt.scheduled_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
                    {appt.patient_age && ` • Age: ${appt.patient_age}`}
                    {appt.patient_gender && ` • ${appt.patient_gender}`}
                  </p>
                  {appt.chief_complaint && (
                    <p className="text-sm text-gray-400 mt-1">💬 {appt.chief_complaint}</p>
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0 flex-wrap">
                  {/* View patient details */}
                  <Link
                    to={`/doctor/patient/${appt.patient_id}`}
                    className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-xs font-medium hover:bg-gray-200 transition-colors"
                  >
                    Patient Details
                  </Link>

                  {/* Status actions */}
                  {(appt.status === 'pending' || appt.status === 'confirmed') && (
                    <>
                      {appt.status === 'pending' && (
                        <button
                          onClick={() => updateStatus(appt.id, 'confirmed')}
                          disabled={actionLoading === appt.id}
                          className="px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700 disabled:opacity-50"
                        >
                          ✓ Confirm
                        </button>
                      )}
                      <button
                        onClick={() => updateStatus(appt.id, 'cancelled')}
                        disabled={actionLoading === appt.id}
                        className="px-3 py-1.5 bg-rose-100 text-rose-700 rounded-lg text-xs font-medium hover:bg-rose-200 disabled:opacity-50"
                      >
                        ✗ Cancel
                      </button>
                    </>
                  )}

                  {appt.status === 'confirmed' && (
                    <>
                      <button
                        onClick={() => joinCall(appt.id)}
                        className="px-3 py-1.5 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700"
                      >
                        📹 Join Call
                      </button>
                      <button
                        onClick={() => updateStatus(appt.id, 'completed')}
                        disabled={actionLoading === appt.id}
                        className="px-3 py-1.5 bg-primary-600 text-white rounded-lg text-xs font-medium hover:bg-primary-700 disabled:opacity-50"
                      >
                        ✓ Complete
                      </button>
                      <button
                        onClick={() => setPrescriptionModal(appt)}
                        className="px-3 py-1.5 bg-amber-100 text-amber-700 rounded-lg text-xs font-medium hover:bg-amber-200"
                      >
                        📝 Prescribe
                      </button>
                    </>
                  )}

                  {appt.status === 'completed' && (
                    <button
                      onClick={() => setPrescriptionModal(appt)}
                      className="px-3 py-1.5 bg-amber-100 text-amber-700 rounded-lg text-xs font-medium hover:bg-amber-200"
                    >
                      📝 Write Prescription
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Video Modal */}
      <Modal open={!!videoModal} onClose={() => setVideoModal(null)} title="Video Consultation">
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
            <p className="text-xs text-gray-400 mt-3">Room: {videoModal.room_name}</p>
          </div>
        )}
      </Modal>

      {/* Prescription Modal */}
      <Modal
        open={!!prescriptionModal}
        onClose={() => setPrescriptionModal(null)}
        title={`Prescription for ${prescriptionModal?.patient_name}`}
        maxWidth="max-w-2xl"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Diagnosis</label>
            <input
              type="text"
              value={rxForm.diagnosis}
              onChange={(e) => setRxForm({ ...rxForm, diagnosis: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="e.g., Upper respiratory infection"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">Medicines</label>
              <button onClick={addMedicine} className="text-xs text-primary-600 hover:underline font-medium">
                + Add Medicine
              </button>
            </div>
            {rxForm.medicines.map((med, i) => (
              <div key={i} className="bg-gray-50 rounded-xl p-3 mb-2">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">Medicine {i + 1}</span>
                  {rxForm.medicines.length > 1 && (
                    <button onClick={() => removeMedicine(i)} className="text-xs text-rose-500">Remove</button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="text"
                    value={med.name}
                    onChange={(e) => updateMedicine(i, 'name', e.target.value)}
                    className="px-2 py-1.5 border border-gray-200 rounded-lg text-sm"
                    placeholder="Medicine name *"
                  />
                  <input
                    type="text"
                    value={med.dosage}
                    onChange={(e) => updateMedicine(i, 'dosage', e.target.value)}
                    className="px-2 py-1.5 border border-gray-200 rounded-lg text-sm"
                    placeholder="Dosage (e.g., 500mg)"
                  />
                  <input
                    type="text"
                    value={med.frequency}
                    onChange={(e) => updateMedicine(i, 'frequency', e.target.value)}
                    className="px-2 py-1.5 border border-gray-200 rounded-lg text-sm"
                    placeholder="Frequency (e.g., 3x/day)"
                  />
                  <input
                    type="number"
                    value={med.duration_days}
                    onChange={(e) => updateMedicine(i, 'duration_days', e.target.value)}
                    className="px-2 py-1.5 border border-gray-200 rounded-lg text-sm"
                    placeholder="Days"
                  />
                </div>
                <input
                  type="text"
                  value={med.instructions}
                  onChange={(e) => updateMedicine(i, 'instructions', e.target.value)}
                  className="w-full px-2 py-1.5 border border-gray-200 rounded-lg text-sm mt-2"
                  placeholder="Special instructions"
                />
              </div>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Advice</label>
            <textarea
              value={rxForm.advice}
              onChange={(e) => setRxForm({ ...rxForm, advice: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500"
              rows={2}
              placeholder="General advice for the patient..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Follow-up Date</label>
            <input
              type="date"
              value={rxForm.follow_up_date}
              onChange={(e) => setRxForm({ ...rxForm, follow_up_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <button
            onClick={submitPrescription}
            disabled={rxSaving}
            className="w-full py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-medium text-sm disabled:opacity-50"
          >
            {rxSaving ? 'Saving...' : 'Save Prescription'}
          </button>
        </div>
      </Modal>
    </div>
  );
}
