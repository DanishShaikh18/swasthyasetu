import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../../api';
import Spinner from '../../components/Spinner';

export default function PatientRecord() {
  const { patientId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get(`/doctors/me/patients/${patientId}`);
        setData(res.data);
      } catch (err) {
        setError(err.message || 'Cannot load patient details');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [patientId]);

  if (loading) return <Spinner />;
  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-rose-500 mb-4">{error}</p>
        <Link to="/doctor/appointments" className="text-primary-600 hover:underline text-sm">← Back to Appointments</Link>
      </div>
    );
  }
  if (!data) return null;

  const { patient, prescriptions } = data;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <Link to="/doctor/appointments" className="text-sm text-primary-600 hover:underline mb-4 inline-block">← Back to Appointments</Link>

      {/* Patient info */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6 mb-6">
        <h1 className="text-xl font-bold text-gray-900 mb-4">Patient Record</h1>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
          <div><span className="text-gray-400">Name</span><p className="font-medium text-gray-900">{patient.full_name}</p></div>
          <div><span className="text-gray-400">Gender</span><p className="font-medium text-gray-900">{patient.gender || '—'}</p></div>
          <div><span className="text-gray-400">DOB</span><p className="font-medium text-gray-900">{patient.date_of_birth || '—'}</p></div>
          <div><span className="text-gray-400">Blood Group</span><p className="font-medium text-gray-900">{patient.blood_group || '—'}</p></div>
          <div><span className="text-gray-400">Location</span><p className="font-medium text-gray-900">{[patient.village, patient.district, patient.state].filter(Boolean).join(', ') || '—'}</p></div>
        </div>

        {(patient.allergies?.length > 0 || patient.chronic_conditions?.length > 0) && (
          <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {patient.allergies?.length > 0 && (
              <div>
                <span className="text-xs font-medium text-gray-400 uppercase">Allergies</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {patient.allergies.map((a, i) => (
                    <span key={i} className="px-2 py-0.5 bg-rose-50 text-rose-600 rounded-md text-xs">{a}</span>
                  ))}
                </div>
              </div>
            )}
            {patient.chronic_conditions?.length > 0 && (
              <div>
                <span className="text-xs font-medium text-gray-400 uppercase">Chronic Conditions</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {patient.chronic_conditions.map((c, i) => (
                    <span key={i} className="px-2 py-0.5 bg-amber-50 text-amber-600 rounded-md text-xs">{c}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Prescriptions history */}
      <div className="bg-white rounded-2xl border border-gray-100 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Prescription History</h2>
        {prescriptions?.length === 0 ? (
          <p className="text-center py-8 text-gray-400 text-sm">No previous prescriptions</p>
        ) : (
          <div className="space-y-3">
            {prescriptions?.map((rx) => (
              <div key={rx.id} className="p-4 bg-gray-50 rounded-xl">
                <div className="flex items-start justify-between mb-2">
                  <p className="text-sm font-medium text-gray-900">{rx.diagnosis || 'No diagnosis'}</p>
                  <span className="text-xs text-gray-400">
                    {new Date(rx.created_at).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                  </span>
                </div>
                {rx.medicines?.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {rx.medicines.map((m, i) => (
                      <span key={i} className="px-2 py-0.5 bg-white border border-gray-200 rounded-md text-xs text-gray-600">
                        {m.name || m.medicine_name}
                      </span>
                    ))}
                  </div>
                )}
                {rx.advice && <p className="text-xs text-gray-500 mt-2">💡 {rx.advice}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
