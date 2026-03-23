import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getInventory, addInventoryItem, updateInventoryItem } from '../api'

export default function Inventory() {
  const [params] = useSearchParams()
  const [items, setItems] = useState([])
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [showAdd, setShowAdd] = useState(false)
  const [addForm, setAddForm] = useState({ medicine_name: '', generic_name: '', category: '', quantity_in_stock: 0, price_per_unit: 0, unit: 'tablet', requires_prescription: false })

  useEffect(() => { fetchInventory() }, [search, page])

  const fetchInventory = async () => {
    setLoading(true)
    try {
      const r = await getInventory({ search: search || undefined, page, limit: 50 })
      let fetched = r.data?.data?.items || []
      if (params.get('filter') === 'low') fetched = fetched.filter(i => i.quantity_in_stock > 0 && i.quantity_in_stock < 20)
      setItems(fetched)
    } catch {} finally { setLoading(false) }
  }

  const handleEdit = (item) => { setEditingId(item.id); setEditForm({ quantity_in_stock: item.quantity_in_stock, price_per_unit: item.price_per_unit }) }

  const handleSave = async (id) => {
    try { await updateInventoryItem(id, editForm); setEditingId(null); fetchInventory() } catch {}
  }

  const handleAdd = async () => {
    try { await addInventoryItem(addForm); setShowAdd(false); setAddForm({ medicine_name: '', generic_name: '', category: '', quantity_in_stock: 0, price_per_unit: 0, unit: 'tablet', requires_prescription: false }); fetchInventory() } catch {}
  }

  return (
    <div className="p-6 max-w-5xl">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <h1 className="text-2xl font-bold">Medicine Inventory</h1>
        <button onClick={() => setShowAdd(true)} className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium min-h-[40px]">+ Add Medicine</button>
      </div>

      {/* Search */}
      <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search medicines..."
        className="w-full p-3 rounded-xl border border-border bg-surface mb-4" />

      {/* Add Form */}
      {showAdd && (
        <div className="bg-primary-light rounded-2xl p-5 border border-primary/20 mb-4">
          <h3 className="font-semibold mb-3">Add New Medicine</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input value={addForm.medicine_name} onChange={e => setAddForm(f => ({...f, medicine_name: e.target.value}))} placeholder="Medicine Name *"
              className="p-2.5 rounded-xl border border-border bg-surface text-sm" />
            <input value={addForm.generic_name} onChange={e => setAddForm(f => ({...f, generic_name: e.target.value}))} placeholder="Generic Name"
              className="p-2.5 rounded-xl border border-border bg-surface text-sm" />
            <input value={addForm.category} onChange={e => setAddForm(f => ({...f, category: e.target.value}))} placeholder="Category"
              className="p-2.5 rounded-xl border border-border bg-surface text-sm" />
            <input type="number" value={addForm.quantity_in_stock} onChange={e => setAddForm(f => ({...f, quantity_in_stock: parseInt(e.target.value) || 0}))} placeholder="Quantity"
              className="p-2.5 rounded-xl border border-border bg-surface text-sm" />
            <input type="number" step="0.01" value={addForm.price_per_unit} onChange={e => setAddForm(f => ({...f, price_per_unit: parseFloat(e.target.value) || 0}))} placeholder="Price"
              className="p-2.5 rounded-xl border border-border bg-surface text-sm" />
            <select value={addForm.unit} onChange={e => setAddForm(f => ({...f, unit: e.target.value}))}
              className="p-2.5 rounded-xl border border-border bg-surface text-sm">
              <option value="tablet">Tablet</option><option value="capsule">Capsule</option>
              <option value="bottle">Bottle</option><option value="sachet">Sachet</option>
              <option value="inhaler">Inhaler</option><option value="vial">Vial</option>
              <option value="roll">Roll</option><option value="pack">Pack</option>
            </select>
          </div>
          <div className="flex items-center gap-2 mt-3">
            <input type="checkbox" checked={addForm.requires_prescription} onChange={e => setAddForm(f => ({...f, requires_prescription: e.target.checked}))} />
            <label className="text-sm">Requires Prescription</label>
          </div>
          <div className="flex gap-2 mt-3">
            <button onClick={handleAdd} className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-medium min-h-[40px]">Add</button>
            <button onClick={() => setShowAdd(false)} className="px-4 py-2 bg-surface border border-border rounded-xl text-sm min-h-[40px]">Cancel</button>
          </div>
        </div>
      )}

      {/* Table */}
      {loading ? (
        <div className="space-y-2">{[1,2,3,4,5].map(i => <div key={i} className="h-12 bg-amber-50 rounded-lg animate-pulse" />)}</div>
      ) : (
        <div className="bg-surface rounded-2xl border border-border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-primary-light/50 text-text-mid text-left">
                  <th className="p-3 font-medium">Medicine</th>
                  <th className="p-3 font-medium">Generic</th>
                  <th className="p-3 font-medium">Category</th>
                  <th className="p-3 font-medium">Stock</th>
                  <th className="p-3 font-medium">Price (₹)</th>
                  <th className="p-3 font-medium">Rx</th>
                  <th className="p-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id} className="border-t border-border hover:bg-primary-light/20">
                    <td className="p-3 font-medium">{item.medicine_name}</td>
                    <td className="p-3 text-text-muted">{item.generic_name || '—'}</td>
                    <td className="p-3">{item.category || '—'}</td>
                    <td className="p-3">
                      {editingId === item.id ? (
                        <input type="number" value={editForm.quantity_in_stock} onChange={e => setEditForm(f => ({...f, quantity_in_stock: parseInt(e.target.value) || 0}))}
                          className="w-20 p-1 border border-border rounded text-sm" />
                      ) : (
                        <span className={`font-medium ${item.quantity_in_stock === 0 ? 'text-danger' : item.quantity_in_stock < 20 ? 'text-warning' : 'text-success'}`}>
                          {item.quantity_in_stock}
                        </span>
                      )}
                    </td>
                    <td className="p-3">
                      {editingId === item.id ? (
                        <input type="number" step="0.01" value={editForm.price_per_unit} onChange={e => setEditForm(f => ({...f, price_per_unit: parseFloat(e.target.value) || 0}))}
                          className="w-20 p-1 border border-border rounded text-sm" />
                      ) : <span>₹{item.price_per_unit || '—'}</span>}
                    </td>
                    <td className="p-3">{item.requires_prescription ? '✓' : '—'}</td>
                    <td className="p-3">
                      {editingId === item.id ? (
                        <div className="flex gap-1">
                          <button onClick={() => handleSave(item.id)} className="px-2 py-1 bg-success text-white rounded text-xs">Save</button>
                          <button onClick={() => setEditingId(null)} className="px-2 py-1 bg-surface border border-border rounded text-xs">✕</button>
                        </div>
                      ) : (
                        <button onClick={() => handleEdit(item)} className="px-2 py-1 bg-primary-light text-primary rounded text-xs font-medium">Edit</button>
                      )}
                    </td>
                  </tr>
                ))}
                {items.length === 0 && <tr><td colSpan={7} className="p-8 text-center text-text-muted">No medicines found</td></tr>}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pagination */}
      <div className="flex gap-2 mt-4 justify-center">
        <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
          className="px-4 py-2 bg-surface border border-border rounded-xl text-sm disabled:opacity-50 min-h-[40px]">← Prev</button>
        <span className="px-4 py-2 text-sm text-text-mid">Page {page}</span>
        <button onClick={() => setPage(p => p + 1)} disabled={items.length < 50}
          className="px-4 py-2 bg-surface border border-border rounded-xl text-sm disabled:opacity-50 min-h-[40px]">Next →</button>
      </div>
    </div>
  )
}
