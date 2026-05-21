/** Reusable status badge */
const statusColors = {
  pending: 'bg-amber-50 text-amber-700 border-amber-200',
  confirmed: 'bg-primary-50 text-primary-700 border-primary-200',
  completed: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  cancelled: 'bg-rose-50 text-rose-700 border-rose-200',
  no_show: 'bg-gray-100 text-gray-600 border-gray-200',
  available: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  booked: 'bg-primary-50 text-primary-700 border-primary-200',
};

export default function StatusBadge({ status }) {
  const color = statusColors[status] || 'bg-gray-100 text-gray-600 border-gray-200';
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${color}`}>
      {status?.replace('_', ' ')}
    </span>
  );
}
