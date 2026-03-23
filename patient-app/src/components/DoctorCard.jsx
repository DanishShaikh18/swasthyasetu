export default function DoctorCard({ doctor, onBook }) {
  return (
    <div className="bg-surface rounded-2xl p-4 border border-border shadow-sm">
      <div className="flex items-start gap-3">
        <div className="w-12 h-12 rounded-full bg-primary-light flex items-center justify-center text-xl flex-shrink-0">
          👨‍⚕️
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-text-dark truncate">{doctor.full_name}</h3>
          <p className="text-sm text-primary font-medium">{doctor.specialization}</p>
          <p className="text-xs text-text-muted mt-1">{doctor.hospital_name}</p>
          <div className="flex flex-wrap gap-1 mt-2">
            {(doctor.languages_spoken || []).map((l) => (
              <span key={l} className="text-xs bg-primary-light text-primary px-2 py-0.5 rounded-full">{l}</span>
            ))}
          </div>
          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-3 text-sm text-text-mid">
              <span>{doctor.experience_years} yrs</span>
              <span>₹{doctor.consultation_fee || 'Free'}</span>
            </div>
            {doctor.is_available && (
              <span className="text-xs bg-urgency-green text-white px-2 py-1 rounded-full">● Online</span>
            )}
          </div>
        </div>
      </div>
      {onBook && (
        <button onClick={() => onBook(doctor)}
          className="w-full mt-3 py-3 bg-primary text-white rounded-xl font-medium text-sm hover:bg-primary-dark active:scale-[0.98] transition-all min-h-[48px]">
          Book Appointment
        </button>
      )}
    </div>
  )
}
