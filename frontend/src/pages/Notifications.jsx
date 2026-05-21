import { useState, useEffect } from 'react';
import api from '../api';
import Spinner from '../components/Spinner';
import EmptyState from '../components/EmptyState';

export default function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get('/content/notifications/me?limit=50');
        setNotifications(res.data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const markRead = async (id) => {
    try {
      await api.patch(`/content/notifications/${id}/read`);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Notifications</h1>

      {notifications.length === 0 ? (
        <EmptyState icon="🔔" title="No notifications" description="You're all caught up!" />
      ) : (
        <div className="space-y-2">
          {notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => !n.is_read && markRead(n.id)}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                n.is_read
                  ? 'bg-white border-gray-100'
                  : 'bg-primary-50 border-primary-200 hover:bg-primary-100'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className={`text-sm font-medium ${n.is_read ? 'text-gray-700' : 'text-gray-900'}`}>
                    {n.title}
                  </h3>
                  <p className="text-sm text-gray-500 mt-0.5">{n.body}</p>
                </div>
                {!n.is_read && (
                  <span className="w-2 h-2 bg-primary-500 rounded-full shrink-0 mt-1.5" />
                )}
              </div>
              <p className="text-xs text-gray-400 mt-2">
                {new Date(n.created_at).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
