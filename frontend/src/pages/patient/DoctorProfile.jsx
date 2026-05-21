import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api';
import Spinner from '../../components/Spinner';
import Modal from '../../components/Modal';

export default function DoctorProfile() {
  const { doctorId } = useParams();
  const navigate = useNavigate();
  const [doctor, setDoctor] = useState(null);
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [complaint, setComplaint] = useState('');
  const [booking, setBooking] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [bookingResult, setBookingResult] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const [docRes, slotsRes] = await Promise.all([
          api.get(`/doctors?limit=50`),
          api.get(`/doctors/${doctorId}/slots?days=14`),
        ]);
        // Find this doctor from list
        const docs = docRes.data?.items || [];
        const found = docs.find((d) => d.id === doctorId);
        setDoctor(found || null);
        setSlots(slotsRes.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [doctorId]);

  // Group slots by date
  const slotsByDate = {};
  slots.forEach((s) => {
    // The backend wrongly attaches UTC to naive local times. 
    // Strip the timezone so JS parses it as local time.
    const localTimeStr = s.slot_time.replace(/(Z|\+00:00)$/, '');
    const date = new Date(localTimeStr).toLocaleDateString('en-IN', {
      weekday: 'short', month: 'short', day: 'numeric',
    });
    if (!slotsByDate[date]) slotsByDate[date] = [];
    slotsByDate[date].push({ ...s, displayDate: new Date(localTimeStr) });
  });

  const handleBook = async () => {
    if (!selectedSlot) return;
    setBooking(true);
    try {
      const res = await api.post('/patients/appointments', {
        doctor_id: doctorId,
        slot_time: selectedSlot.slot_time,
        type: 'video',
        chief_complaint: complaint || null,
      });
      setBookingResult(res.data);
      setShowConfirm(true);
    } catch (err) {
      alert(err.message || 'Booking failed');
    } finally {
      setBooking(false);
    }
  };

  if (loading) return <Spinner />;
  if (!doctor) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-gray-500">Doctor not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      {/* Doctor info */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6">
        <div className="flex items-start gap-5">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center text-primary-700 font-bold text-2xl shrink-0">
            {doctor.full_name?.charAt(0)}
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Dr. {doctor.full_name}</h1>
            <p className="text-primary-600 font-medium">{doctor.specialization}</p>
            {doctor.qualification && <p className="text-sm text-gray-500 mt-0.5">{doctor.qualification}</p>}

            <div className="flex flex-wrap gap-3 mt-3 text-sm text-gray-500">
              {doctor.experience_years > 0 && (
                <span>📋 {doctor.experience_years} years experience</span>
              )}
              {doctor.hospital_name && <span>🏥 {doctor.hospital_name}</span>}
              {doctor.consultation_fee > 0 && (
                <span className="text-emerald-600 font-medium">₹{doctor.consultation_fee} / consultation</span>
              )}
            </div>

            {doctor.bio && (
              <p className="text-sm text-gray-600 mt-3 leading-relaxed">{doctor.bio}</p>
            )}

            {doctor.languages_spoken?.length > 0 && (
              <div className="flex gap-1.5 mt-3">
                {doctor.languages_spoken.map((l) => (
                  <span key={l} className="px-2 py-0.5 bg-gray-100 rounded-md text-xs text-gray-600">{l}</span>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Available slots */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Slots</h2>

        {Object.keys(slotsByDate).length === 0 ? (
          <p className="text-gray-400 text-sm text-center py-8">No available slots for the next 14 days</p>
        ) : (
          <div className="space-y-4">
            {Object.entries(slotsByDate).map(([date, dateSlots]) => (
              <div key={date}>
                <p className="text-sm font-medium text-gray-600 mb-2">{date}</p>
                <div className="flex flex-wrap gap-2">
                  {dateSlots.map((slot) => {
                    const time = slot.displayDate.toLocaleTimeString('en-IN', {
                      hour: '2-digit', minute: '2-digit',
                    });
                    const isSelected = selectedSlot?.id === slot.id;
                    return (
                      <button
                        key={slot.id}
                        onClick={() => setSelectedSlot(slot)}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-all ${
                          isSelected
                            ? 'bg-primary-600 text-white border-primary-600'
                            : 'bg-white text-gray-700 border-gray-200 hover:border-primary-300 hover:bg-primary-50'
                        }`}
                      >
                        {time}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Booking section */}
      {selectedSlot && (
        <div className="bg-white rounded-2xl border border-primary-200 p-6 animate-slide-up">
          <h3 className="font-semibold text-gray-900 mb-3">Book Appointment</h3>
          <p className="text-sm text-gray-600 mb-4">
            📅 {selectedSlot.displayDate.toLocaleString('en-IN', { dateStyle: 'full', timeStyle: 'short' })}
          </p>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Chief Complaint (optional)</label>
            <textarea
              value={complaint}
              onChange={(e) => setComplaint(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none text-sm"
              rows={2}
              placeholder="Describe your symptoms or reason for visit..."
            />
          </div>

          <button
            onClick={handleBook}
            disabled={booking}
            className="w-full py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-medium text-sm hover:from-primary-700 hover:to-primary-800 transition-all disabled:opacity-50 shadow-md shadow-primary-200"
          >
            {booking ? 'Booking...' : 'Confirm Booking'}
          </button>
        </div>
      )}

      {/* Confirmation Modal */}
      <Modal
        open={showConfirm}
        onClose={() => {
          setShowConfirm(false);
          navigate('/patient/appointments');
        }}
        title="Appointment Booked! ✅"
      >
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-100 flex items-center justify-center">
            <span className="text-3xl">✓</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Booking Confirmed!</h3>
          <p className="text-sm text-gray-500 mt-2">
            Your appointment with <strong>Dr. {doctor.full_name}</strong> has been confirmed.
          </p>
          {bookingResult && (
            <p className="text-sm text-gray-500 mt-1">
              📅 {new Date(bookingResult.scheduled_at).toLocaleString('en-IN', { dateStyle: 'full', timeStyle: 'short' })}
            </p>
          )}
          <p className="text-xs text-gray-400 mt-3">
            You will be able to join the video call from your Appointments page.
          </p>
          <button
            onClick={() => {
              setShowConfirm(false);
              navigate('/patient/appointments');
            }}
            className="mt-6 px-6 py-2 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 transition-colors"
          >
            Go to Appointments
          </button>
        </div>
      </Modal>
    </div>
  );
}
