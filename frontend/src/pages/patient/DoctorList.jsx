import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../../api';
import Spinner from '../../components/Spinner';

const SPECIALIZATIONS = [
  'All', 'General Medicine', 'Pediatrics', 'Dermatology', 'Orthopedics',
  'Gynecology', 'ENT', 'Ophthalmology', 'Cardiology', 'Neurology',
  'Psychiatry', 'Dentistry', 'Ayurveda', 'Homeopathy',
];

export default function DoctorList() {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [specFilter, setSpecFilter] = useState('All');

  useEffect(() => {
    loadDoctors();
  }, [specFilter]);

  async function loadDoctors() {
    setLoading(true);
    try {
      let url = '/doctors?limit=50';
      if (specFilter !== 'All') url += `&specialization=${encodeURIComponent(specFilter)}`;
      const res = await api.get(url);
      setDoctors(res.data?.items || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  // Client-side name filter
  const filtered = doctors.filter((d) =>
    d.full_name?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Find a Doctor</h1>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm"
            placeholder="Search doctor by name..."
          />
        </div>
        <select
          value={specFilter}
          onChange={(e) => setSpecFilter(e.target.value)}
          className="px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-primary-500 outline-none bg-white"
        >
          {SPECIALIZATIONS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <Spinner />
      ) : filtered.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-4xl mb-3">🩺</p>
          <p className="text-gray-500">No doctors found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((doc) => (
            <Link
              key={doc.id}
              to={`/patient/doctors/${doc.id}`}
              className="group bg-white rounded-2xl border border-gray-100 p-5 hover:border-primary-200 hover:shadow-lg transition-all"
            >
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center text-primary-700 font-bold text-lg shrink-0">
                  {doc.full_name?.charAt(0) || '?'}
                </div>
                <div className="min-w-0">
                  <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors truncate">
                    Dr. {doc.full_name}
                  </h3>
                  <p className="text-sm text-primary-600 font-medium">{doc.specialization}</p>
                  {doc.qualification && (
                    <p className="text-xs text-gray-400 mt-0.5">{doc.qualification}</p>
                  )}
                </div>
              </div>

              <div className="mt-4 flex flex-wrap gap-2 text-xs">
                {doc.experience_years > 0 && (
                  <span className="px-2 py-1 bg-gray-50 rounded-lg text-gray-500">
                    {doc.experience_years}y exp
                  </span>
                )}
                {doc.hospital_name && (
                  <span className="px-2 py-1 bg-gray-50 rounded-lg text-gray-500 truncate max-w-[140px]">
                    🏥 {doc.hospital_name}
                  </span>
                )}
                {doc.consultation_fee > 0 && (
                  <span className="px-2 py-1 bg-emerald-50 rounded-lg text-emerald-600 font-medium">
                    ₹{doc.consultation_fee}
                  </span>
                )}
              </div>

              <div className="mt-3 flex items-center justify-between">
                <span className={`text-xs font-medium ${doc.is_available ? 'text-emerald-600' : 'text-gray-400'}`}>
                  {doc.is_available ? '🟢 Available' : '⚫ Unavailable'}
                </span>
                <span className="text-xs text-primary-600 group-hover:underline font-medium">
                  View Profile →
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
