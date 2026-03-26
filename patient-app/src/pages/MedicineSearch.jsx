import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { searchPharmacy } from '../api/pharmacy'
import VoiceInput from '../components/VoiceInput'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'

export default function MedicineSearch() {
  const [params] = useSearchParams()
  const [query, setQuery] = useState(params.get('search') || '')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [userLoc, setUserLoc] = useState({ lat: 28.6, lng: 77.2 })
  const { t, i18n } = useTranslation()

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      (pos) => setUserLoc({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => {}
    )
  }, [])

  useEffect(() => {
    if (query.length >= 2) doSearch()
  }, [])

  const doSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const params = { medicine: query, in_stock: true }
      if (userLoc.lat && userLoc.lng) {
        params.lat = userLoc.lat
        params.lng = userLoc.lng
        params.radius_km = 50
      }
      const res = await searchPharmacy(params)
      setResults(res.data?.data || [])
    } catch { setResults([]) }
    finally { setLoading(false) }
  }

  return (
    <div className="px-4 py-4">
      <h1 className="text-xl font-bold text-text-dark mb-3">{t('medicine.title')}</h1>

      <div className="flex gap-2 mb-3">
        <input value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === 'Enter' && doSearch()}
          placeholder={t('medicine.searchPlaceholder')}
          className="flex-1 p-3 rounded-xl border border-border bg-surface text-base min-h-[48px]" />
        <button onClick={doSearch} className="px-4 bg-primary text-white rounded-xl font-medium min-h-[48px]">🔍</button>
      </div>

      <VoiceInput language={i18n.language} onResult={(text) => { setQuery(text); }} />

      {loading && <div className="space-y-3 mt-4">{[1,2,3].map(i => <div key={i} className="skeleton h-28 rounded-2xl" />)}</div>}

      {/* Results List */}
      {!loading && results.length > 0 && (
        <>
          <div className="space-y-3 mt-4">
            {results.map((r, i) => (
              <div key={i} className="bg-surface rounded-2xl p-4 border border-border shadow-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-text-dark">{r.pharmacy_name}</h3>
                    <p className="text-sm text-text-mid">{r.medicine_name}</p>
                    {r.generic_name && <p className="text-xs text-text-muted">({r.generic_name})</p>}
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-medium text-primary">{r.distance_km} {t('medicine.distance')}</span>
                    {r.requires_prescription && (
                      <span className="block text-xs bg-urgency-yellow text-white px-2 py-0.5 rounded-full mt-1">
                        {t('medicine.prescriptionRequired')}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-center justify-between mt-2 text-sm">
                  <span className={r.quantity_in_stock > 0 ? 'text-urgency-green font-medium' : 'text-urgency-red'}>
                    {r.quantity_in_stock > 0 ? `✓ ${t('medicine.inStock')} (${r.quantity_in_stock})` : t('medicine.outOfStock')}
                  </span>
                  {r.price_per_unit && <span className="font-medium">₹{r.price_per_unit}</span>}
                </div>
                <a href={`tel:${r.phone}`}
                  className="mt-3 w-full py-2.5 bg-primary-light text-primary rounded-xl font-medium text-sm flex items-center justify-center gap-1 min-h-[44px]">
                  📞 {t('medicine.callPharmacy')}
                </a>
              </div>
            ))}
          </div>

          {/* Map */}
          <div className="mt-4 rounded-2xl overflow-hidden border border-border">
            <MapContainer center={[userLoc.lat, userLoc.lng]} zoom={11} scrollWheelZoom={false} className="h-[300px]">
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {results.map((r, i) => (
                <Marker key={i} position={[userLoc.lat + (Math.random()-0.5)*0.1, userLoc.lng + (Math.random()-0.5)*0.1]}>
                  <Popup>{r.pharmacy_name}<br/>{r.medicine_name}: ₹{r.price_per_unit}</Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </>
      )}

      {!loading && results.length === 0 && query && (
        <p className="text-center text-text-muted py-8">{t('common.noData')}</p>
      )}
    </div>
  )
}
