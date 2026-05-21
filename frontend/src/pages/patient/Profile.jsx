import { useState, useEffect } from 'react';
import api from '../../api';
import Spinner from '../../components/Spinner';

export default function PatientProfile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get('/patients/me');
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
      await api.patch('/patients/me', {
        full_name: profile.full_name,
        date_of_birth: profile.date_of_birth || null,
        gender: profile.gender || null,
        blood_group: profile.blood_group || null,
        village: profile.village || null,
        district: profile.district || null,
        state: profile.state || null,
        emergency_contact_name: profile.emergency_contact_name || null,
        emergency_contact_phone: profile.emergency_contact_phone || null,
      });
      setMsg('Profile updated successfully!');
      setTimeout(() => setMsg(''), 3000);
    } catch (err) {
      setMsg(err.message || 'Update failed');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Spinner />;
  if (!profile) return <p className="text-center py-16 text-gray-500">Profile not found</p>;

  const inputClass = "w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm";

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Profile</h1>

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
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input type="email" value={profile.email || ''} disabled className={`${inputClass} bg-gray-50 text-gray-400`} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Phone</label>
              <input type="text" value={profile.phone || ''} disabled className={`${inputClass} bg-gray-50 text-gray-400`} />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Date of Birth</label>
              <input type="date" value={profile.date_of_birth || ''} onChange={set('date_of_birth')} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Gender</label>
              <select value={profile.gender || ''} onChange={set('gender')} className={inputClass}>
                <option value="">Select...</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Blood Group</label>
              <select value={profile.blood_group || ''} onChange={set('blood_group')} className={inputClass}>
                <option value="">Select...</option>
                {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map((bg) => (
                  <option key={bg} value={bg}>{bg}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Village</label>
              <input type="text" value={profile.village || ''} onChange={set('village')} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">District</label>
              <input type="text" value={profile.district || ''} onChange={set('district')} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">State</label>
              <input type="text" value={profile.state || ''} onChange={set('state')} className={inputClass} />
            </div>
          </div>

          <hr className="border-gray-100" />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Emergency Contact Name</label>
              <input type="text" value={profile.emergency_contact_name || ''} onChange={set('emergency_contact_name')} className={inputClass} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Emergency Contact Phone</label>
              <input type="tel" value={profile.emergency_contact_phone || ''} onChange={set('emergency_contact_phone')} className={inputClass} />
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
