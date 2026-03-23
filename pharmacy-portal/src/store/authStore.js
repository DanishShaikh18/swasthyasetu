import { create } from 'zustand'
import { persist } from 'zustand/middleware'
const useAuthStore = create(persist((set) => ({
  accessToken: null, user: null, isAuthenticated: false,
  setAuth: (d) => set({ accessToken: d.access_token, user: { id: d.user_id, role: d.role, fullName: d.full_name }, isAuthenticated: true }),
  setToken: (t) => set({ accessToken: t }),
  logout: () => set({ accessToken: null, user: null, isAuthenticated: false }),
}), { name: 'pharmacy-auth' }))
export default useAuthStore
