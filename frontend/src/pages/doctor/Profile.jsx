import { useState, useEffect } from 'react';
import api from '../../api';
import Spinner from '../../components/Spinner';

const SPECIALIZATIONS = [
  'General Medicine', 'Pediatrics', 'Dermatology', 'Orthopedics',
  'Gynecology', 'ENT', 'Ophthalmology', 'Cardiology', 'Neurology',
  'Psychiatry', 'Dentistry', 'Ayurveda', 'Homeopathy',
];

export default function DoctorProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [toggling, setToggling] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get('/doctors/me/profile');
        setProfile(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const set = (field) => (e) => setProfile({ ...profile, [field]: e.target.value });

  const handleSave = async () => {
    setSaving(true);
    setMsg('');
    try {
      await api.patch('/doctors/me/profile', {
        full_name: profile.full_name,
        specialization: profile.specialization,
        qualification: profile.qualification,
        registration_number: profile.registration_number,
        experience_years: profile.experience_years ? parseInt(profile.experience_years) : null,
        hospital_name: profile.hospital_name,
        bio: profile.bio,
        consultation_fee: profile.consultation_fee ? parseFloat(profile.consultation_fee) : null,
      });
      setMsg('Profile updated successfully!');
      setTimeout(() => setMsg(''), 3000);
    } catch (err) {
      setMsg(err.message || 'Update failed');
    } finally {
      setSaving(false);
    }
  };

  const toggleAvailability = async () => {
    setToggling(true);
    try {
      const res = await api.patch('/doctors/me/availability', {
        is_available: !profile.is_available,
      });
      setProfile({ ...profile, is_available: res.data?.is_available ?? !profile.is_available });
    } catch (err) {
      alert(err.message || 'Failed to toggle');
    } finally {
      setToggling(false);
    }
  };

  if (loading) return <Spinner />;
  if (!profile) return <p className="text-center py-16 text-gray-500">Profile not found</p>;

  const inputClass = "w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm";

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Profile</h1>

      {/* Availability toggle */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-6 flex items-center justify-between">
        <div>
          <p className="font-medium text-gray-900">Availability Status</p>
          <p className="text-sm text-gray-500">
            {profile.is_available ? '🟢 You are visible to patients' : '🔴 You are hidden from listings'}
          </p>
        </div>
        <button
          onClick={toggleAvailability}
          disabled={toggling}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
            profile.is_available
              ? 'bg-rose-100 text-rose-700 hover:bg-rose-200'
              : 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200'
          }`}
        >
          {toggling ? '...' : profile.is_available ? 'Go Offline' : 'Go Online'}
        </button>
      </div>

      {!profile.is_approved && (
        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-2xl">
          <p className="text-amber-800 text-sm font-medium">⏳ Your account is pending admin approval</p>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-gray-100 p-6">
        {msg && (
          <div className={`mb-4 p-3 rounded-xl text-sm ${msg.includes('success') ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'}`}>
            {msg}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
            <input type="text" value={profile.full_name || ''} onChange={set('full_name')} className={inputClass} />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Specialization</label>
              <select value={profile.specialization || ''} onChange={set('specialization')} className={inputClass}>
                {SPECIALIZATIONS.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Qualification</label>
              <input type="text" value={profile.qualification || ''} onChange={set('qualification')} className={inputClass} />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Registration No.</label>
              <input type="text" value={profile.registration_number || ''} onChange={set('registration_number')} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Experience (years)</label>
              <input type="number" min="0" value={profile.experience_years || ''} onChange={set('experience_years')} className={inputClass} />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Hospital / Clinic</label>
              <input type="text" value={profile.hospital_name || ''} onChange={set('hospital_name')} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Consultation Fee (₹)</label>
              <input type="number" min="0" value={profile.consultation_fee || ''} onChange={set('consultation_fee')} className={inputClass} />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Bio</label>
            <textarea value={profile.bio || ''} onChange={set('bio')} className={inputClass} rows={3} placeholder="Brief about yourself..." />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input type="email" value={profile.email || ''} disabled className={`${inputClass} bg-gray-50 text-gray-400`} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">User ID</label>
              <input type="text" value={profile.user_id || ''} disabled className={`${inputClass} bg-gray-50 text-gray-400 text-xs`} />
            </div>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-medium text-sm hover:from-primary-700 hover:to-primary-800 transition-all disabled:opacity-50 shadow-md shadow-primary-200"
          >
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </div>
    </div>
  );
}
