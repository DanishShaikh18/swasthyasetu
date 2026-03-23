import axios from 'axios'
import useAuthStore from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({ baseURL: API_URL, withCredentials: true })

client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401 && !err.config._retry) {
      err.config._retry = true
      try {
        const res = await axios.post(`${API_URL}/api/v1/auth/refresh`, {}, { withCredentials: true })
        const newToken = res.data?.data?.access_token
        if (newToken) {
          useAuthStore.getState().setToken(newToken)
          err.config.headers.Authorization = `Bearer ${newToken}`
          return client(err.config)
        }
      } catch {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default client
