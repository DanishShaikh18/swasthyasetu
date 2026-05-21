export default function Spinner({ size = 'md', className = '' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' };
  return (
    <div className={`flex justify-center items-center py-12 ${className}`}>
      <div className={`${sizes[size]} border-3 border-gray-200 border-t-primary-500 rounded-full animate-spin`} />
    </div>
  );
}

export function PageLoader() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <Spinner size="lg" />
      <p className="mt-4 text-gray-500 text-sm">Loading...</p>
    </div>
  );
}
