import { useState, useEffect } from 'react';
import api from '../../api';
import Spinner from '../../components/Spinner';
import EmptyState from '../../components/EmptyState';

export default function Prescriptions() {
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get('/patients/me/prescriptions?limit=50');
        setPrescriptions(res.data?.items || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Spinner />;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">My Prescriptions</h1>

      {prescriptions.length === 0 ? (
        <EmptyState icon="💊" title="No prescriptions yet" description="Your prescriptions will appear here after consultations." />
      ) : (
        <div className="space-y-4">
          {prescriptions.map((rx) => (
            <div key={rx.id} className="bg-white rounded-2xl border border-gray-100 p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{rx.doctor_name}</h3>
                  <p className="text-sm text-primary-600">{rx.doctor_specialization}</p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {new Date(rx.created_at).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                  </p>
                </div>
                {rx.is_active && (
                  <span className="px-2 py-0.5 bg-emerald-50 text-emerald-600 rounded-full text-xs font-medium border border-emerald-200">
                    Active
                  </span>
                )}
              </div>

              {rx.diagnosis && (
                <div className="mb-3">
                  <p className="text-xs font-medium text-gray-500 uppercase mb-1">Diagnosis</p>
                  <p className="text-sm text-gray-700">{rx.diagnosis}</p>
                </div>
              )}

              {rx.medicines?.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs font-medium text-gray-500 uppercase mb-2">Medicines</p>
                  <div className="space-y-2">
                    {rx.medicines.map((med, i) => (
                      <div key={i} className="bg-gray-50 rounded-xl p-3 text-sm">
                        <span className="font-medium text-gray-900">{med.name || med.medicine_name}</span>
                        {med.dosage && <span className="text-gray-500 ml-2">• {med.dosage}</span>}
                        {med.frequency && <span className="text-gray-500 ml-2">• {med.frequency}</span>}
                        {med.duration_days && <span className="text-gray-500 ml-2">• {med.duration_days} days</span>}
                        {med.instructions && (
                          <p className="text-xs text-gray-400 mt-1">📌 {med.instructions}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {rx.advice && (
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase mb-1">Advice</p>
                  <p className="text-sm text-gray-700">{rx.advice}</p>
                </div>
              )}

              {rx.follow_up_date && (
                <p className="text-xs text-amber-600 mt-3 font-medium">
                  📅 Follow-up: {rx.follow_up_date}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
