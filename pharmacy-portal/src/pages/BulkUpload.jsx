import { useState, useRef } from 'react'
import { bulkUpload } from '../api'

export default function BulkUpload() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef()

  const handleUpload = async () => {
    if (!file) return
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await bulkUpload(file)
      setResult(res.data?.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="p-6 max-w-3xl">
      <h1 className="text-2xl font-bold mb-4">Bulk Upload Inventory</h1>

      {/* Instructions */}
      <div className="bg-primary-light rounded-2xl p-5 border border-primary/20 mb-6">
        <h3 className="font-semibold text-primary mb-2">📋 CSV Format Instructions</h3>
        <p className="text-sm text-text-mid mb-3">Upload a CSV file with the following columns:</p>
        <div className="bg-surface rounded-xl p-3 font-mono text-xs overflow-x-auto">
          <p className="font-semibold">medicine_name,generic_name,category,quantity_in_stock,price_per_unit,unit,requires_prescription</p>
          <p className="text-text-muted mt-1">Paracetamol 500mg,Acetaminophen,Analgesic,500,2.00,tablet,false</p>
          <p className="text-text-muted">Amoxicillin 500mg,Amoxicillin,Antibiotic,200,8.50,capsule,true</p>
        </div>
        <ul className="text-xs text-text-mid mt-3 space-y-1">
          <li>• If a medicine already exists (by name), it will be <strong>updated</strong>.</li>
          <li>• New medicines will be <strong>inserted</strong>.</li>
          <li>• Errors are reported per row (first 50 shown).</li>
        </ul>
      </div>

      {/* Upload Zone */}
      <div className="bg-surface rounded-2xl p-6 border-2 border-dashed border-border text-center cursor-pointer hover:border-primary/50 transition-colors"
        onClick={() => fileRef.current?.click()}>
        <input ref={fileRef} type="file" accept=".csv" onChange={e => setFile(e.target.files[0])} className="hidden" />
        {file ? (
          <div>
            <span className="text-3xl">📄</span>
            <p className="font-medium mt-2">{file.name}</p>
            <p className="text-xs text-text-muted">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <div>
            <span className="text-4xl">📤</span>
            <p className="font-medium mt-2">Click to select CSV file</p>
            <p className="text-xs text-text-muted mt-1">Maximum recommended: 1000 rows</p>
          </div>
        )}
      </div>

      <button onClick={handleUpload} disabled={!file || loading}
        className="w-full mt-4 py-3 bg-primary text-white rounded-xl font-semibold disabled:opacity-50 min-h-[48px]">
        {loading ? 'Uploading...' : 'Upload & Process'}
      </button>

      {error && <p className="text-danger text-sm mt-3 p-3 bg-red-50 rounded-xl">{error}</p>}

      {/* Results */}
      {result && (
        <div className="mt-6 bg-surface rounded-2xl p-5 border border-border">
          <h3 className="font-semibold mb-3">Upload Results</h3>
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center p-3 bg-green-50 rounded-xl">
              <p className="text-2xl font-bold text-success">{result.inserted}</p>
              <p className="text-xs text-text-muted">Inserted</p>
            </div>
            <div className="text-center p-3 bg-blue-50 rounded-xl">
              <p className="text-2xl font-bold text-blue-600">{result.updated}</p>
              <p className="text-xs text-text-muted">Updated</p>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-xl">
              <p className="text-2xl font-bold text-danger">{(result.errors || []).length}</p>
              <p className="text-xs text-text-muted">Errors</p>
            </div>
          </div>

          {result.errors?.length > 0 && (
            <div className="mt-3">
              <h4 className="text-sm font-medium text-danger mb-2">Errors:</h4>
              <div className="max-h-40 overflow-y-auto bg-red-50 rounded-xl p-3 text-xs space-y-1">
                {result.errors.map((err, i) => (
                  <p key={i}>Row {err.row}: {err.error}</p>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
