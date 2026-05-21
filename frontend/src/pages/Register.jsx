import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';

const SPECIALIZATIONS = [
  'General Medicine', 'Pediatrics', 'Dermatology', 'Orthopedics',
  'Gynecology', 'ENT', 'Ophthalmology', 'Cardiology', 'Neurology',
  'Psychiatry', 'Dentistry', 'Ayurveda', 'Homeopathy',
];

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const isDoctorPort = window.location.port === '5174';
  const role = isDoctorPort ? 'doctor' : 'patient';
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    full_name: '', email: '', phone: '', password: '',
    // Doctor fields
    specialization: '', qualification: '', registration_number: '',
    experience_years: '', hospital_name: '', bio: '',
  });

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = {
        full_name: form.full_name,
        email: form.email,
        phone: form.phone,
        password: form.password,
        role,
        preferred_language: 'en',
      };
      if (role === 'doctor') {
        payload.specialization = form.specialization;
        payload.qualification = form.qualification;
        payload.registration_number = form.registration_number;
        payload.experience_years = form.experience_years ? parseInt(form.experience_years) : null;
        payload.hospital_name = form.hospital_name;
        payload.bio = form.bio;
      }
      const user = await register(payload);
      if (user.role === 'doctor') navigate('/doctor/dashboard');
      else navigate('/patient/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const inputClass = "w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all text-sm";

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-emerald-50 px-4 py-12">
      <div className="w-full max-w-lg animate-fade-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 mb-4">
            <span className="text-white font-bold text-xl">SS</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            Create {isDoctorPort ? 'Doctor' : 'Patient'} Account
          </h1>
          <p className="text-gray-500 mt-1">Join SwasthyaSetu</p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg shadow-gray-200/50 p-8 border border-gray-100">

          {error && (
            <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Full Name *</label>
              <input type="text" required value={form.full_name} onChange={set('full_name')} className={inputClass} placeholder="Your full name" />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Email *</label>
                <input type="email" required value={form.email} onChange={set('email')} className={inputClass} placeholder="you@example.com" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Phone *</label>
                <input type="tel" required value={form.phone} onChange={set('phone')} className={inputClass} placeholder="9876543210" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password *</label>
              <input type="password" required minLength={6} value={form.password} onChange={set('password')} className={inputClass} placeholder="Min 6 characters" />
            </div>

            {role === 'doctor' && (
              <>
                <hr className="my-2 border-gray-100" />
                <p className="text-sm font-medium text-gray-500">Doctor Details</p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Specialization *</label>
                    <select required value={form.specialization} onChange={set('specialization')} className={inputClass}>
                      <option value="">Select...</option>
                      {SPECIALIZATIONS.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Qualification</label>
                    <input type="text" value={form.qualification} onChange={set('qualification')} className={inputClass} placeholder="MBBS, MD..." />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Registration No.</label>
                    <input type="text" value={form.registration_number} onChange={set('registration_number')} className={inputClass} placeholder="Medical council number" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Experience (years)</label>
                    <input type="number" min="0" value={form.experience_years} onChange={set('experience_years')} className={inputClass} placeholder="5" />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Hospital / Clinic</label>
                  <input type="text" value={form.hospital_name} onChange={set('hospital_name')} className={inputClass} placeholder="Hospital name" />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Bio</label>
                  <textarea value={form.bio} onChange={set('bio')} className={inputClass} rows={2} placeholder="Brief about yourself..." />
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-medium text-sm hover:from-primary-700 hover:to-primary-800 transition-all disabled:opacity-50 shadow-md shadow-primary-200"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 font-medium hover:underline">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
