import axios from 'axios'
import useAuthStore from "./store/authStore";

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const client = axios.create({ baseURL: API, withCredentials: true })

client.interceptors.request.use(c => {
  const t = useAuthStore.getState().accessToken
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})

client.interceptors.response.use(r => r, async err => {
  if (err.response?.status === 401 && !err.config._retry) {
    err.config._retry = true
    try {
      const r = await axios.post(`${API}/api/v1/auth/refresh`, {}, { withCredentials: true })
      const nt = r.data?.data?.access_token
      if (nt) { useAuthStore.getState().setToken(nt); err.config.headers.Authorization = `Bearer ${nt}`; return client(err.config) }
    } catch { useAuthStore.getState().logout(); window.location.href = '/login' }
  }
  return Promise.reject(err)
})

export default client

export const login = (d) => client.post('/api/v1/auth/login', d)
export const logout = () => client.post('/api/v1/auth/logout')
export const getProfile = () => client.get('/api/v1/pharmacy/me/profile')
export const updateProfile = (d) => client.patch('/api/v1/pharmacy/me/profile', d)
export const toggleStatus = (d) => client.patch('/api/v1/pharmacy/me/status', d)
export const getInventory = (p) => client.get('/api/v1/pharmacy/me/inventory', { params: p })
export const addInventoryItem = (d) => client.post('/api/v1/pharmacy/me/inventory', d)
export const updateInventoryItem = (id, d) => client.patch(`/api/v1/pharmacy/me/inventory/${id}`, d)
export const bulkUpload = (file) => {
  const fd = new FormData(); fd.append('file', file)
  return client.post('/api/v1/pharmacy/me/inventory/bulk', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}
