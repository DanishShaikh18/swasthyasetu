import { useState, useEffect } from 'react';
import api from '../../api';
import Spinner from '../../components/Spinner';

const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

export default function DoctorSlots() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [generatedSlots, setGeneratedSlots] = useState([]);
  const [form, setForm] = useState({
    day_of_week: 1,
    start_time: '09:00',
    end_time: '17:00',
    slot_duration_min: 15,
  });

  const loadSlots = async () => {
    try {
      const [resTemplates, resProfile] = await Promise.all([
        api.get('/doctors/me/slots'),
        api.get('/doctors/me/profile')
      ]);
      setTemplates(resTemplates.data || []);
      
      if (resProfile.data?.id) {
        const resGenerated = await api.get(`/doctors/${resProfile.data.id}/slots?days=30`);
        setGeneratedSlots(resGenerated.data || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSlots();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      await api.post('/doctors/me/slots', {
        day_of_week: parseInt(form.day_of_week),
        start_time: form.start_time,
        end_time: form.end_time,
        slot_duration_min: parseInt(form.slot_duration_min),
      });
      await loadSlots();
      alert('Slot template created! Individual slots generated for 30 days.');
    } catch (err) {
      alert(err.message || 'Failed to create slot');
    } finally {
      setCreating(false);
    }
  };

  // Group templates by day
  const byDay = {};
  templates.forEach((t) => {
    const day = DAYS[t.day_of_week] || `Day ${t.day_of_week}`;
    if (!byDay[day]) byDay[day] = [];
    byDay[day].push(t);
  });

  if (loading) return <Spinner />;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Slot Management</h1>

      {/* Create slot form */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">1. Set Recurring Weekly Schedule</h2>
        <div className="p-3 mb-5 bg-blue-50 border border-blue-100 rounded-xl">
          <p className="text-sm text-blue-800">
            <strong>How it works:</strong> You do not select specific dates here. Instead, you select a <strong>Day of the Week</strong> (e.g., Monday). The system will automatically generate all the individual bookable slots for every Monday for the next 30 days.
          </p>
        </div>

        <form onSubmit={handleCreate} className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Day</label>
              <select
                value={form.day_of_week}
                onChange={(e) => setForm({ ...form, day_of_week: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500 bg-white"
              >
                {DAYS.map((d, i) => (
                  <option key={i} value={i}>{d}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Start Time</label>
              <input
                type="time"
                value={form.start_time}
                onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">End Time</label>
              <input
                type="time"
                value={form.end_time}
                onChange={(e) => setForm({ ...form, end_time: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Duration (min)</label>
              <select
                value={form.slot_duration_min}
                onChange={(e) => setForm({ ...form, slot_duration_min: e.target.value })}
                className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500 bg-white"
              >
                <option value={10}>10 min</option>
                <option value={15}>15 min</option>
                <option value={20}>20 min</option>
                <option value={30}>30 min</option>
                <option value={45}>45 min</option>
                <option value={60}>60 min</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={creating}
            className="px-6 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-medium text-sm hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 shadow-md shadow-primary-200"
          >
            {creating ? 'Creating...' : 'Create Slot Template'}
          </button>
        </form>
      </div>

      {/* Existing templates */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">2. Your Active Weekly Rules</h2>

        {Object.keys(byDay).length === 0 ? (
          <p className="text-center py-8 text-gray-400 text-sm">
            No slot templates created yet. Create your first one above.
          </p>
        ) : (
          <div className="space-y-4">
            {Object.entries(byDay).map(([day, slots]) => (
              <div key={day}>
                <h3 className="text-sm font-medium text-gray-600 mb-2">{day}</h3>
                <div className="flex flex-wrap gap-2">
                  {slots.map((slot) => (
                    <div
                      key={slot.id}
                      className="px-3 py-2 bg-primary-50 border border-primary-200 rounded-xl text-sm"
                    >
                      <span className="text-primary-700 font-medium">
                        {slot.start_time} – {slot.end_time}
                      </span>
                      <span className="text-primary-400 ml-1">({slot.slot_duration_min}min)</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Generated Dates Calendar View */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">3. Upcoming Open Dates (Generated)</h2>
        <p className="text-sm text-gray-500 mb-4">
          These are the actual dates that patients can currently see and book on your profile based on your rules above.
        </p>

        {generatedSlots.length === 0 ? (
          <p className="text-center py-8 text-gray-400 text-sm">
            No active dates generated. Create a weekly rule above to open slots.
          </p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {[...new Set(generatedSlots.map(s => {
               const localTimeStr = s.slot_time.replace(/(Z|\+00:00)$/, '');
               return new Date(localTimeStr).toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' });
            }))].map(dateStr => {
              const count = generatedSlots.filter(s => {
                 const localTimeStr = s.slot_time.replace(/(Z|\+00:00)$/, '');
                 return new Date(localTimeStr).toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' }) === dateStr;
              }).length;
              return (
                <div key={dateStr} className="p-3 border border-gray-200 rounded-xl text-center">
                  <p className="font-semibold text-gray-800 text-sm">{dateStr}</p>
                  <p className="text-xs text-primary-600 mt-1">{count} slots open</p>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
