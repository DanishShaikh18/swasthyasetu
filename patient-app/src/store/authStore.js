import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const useAuthStore = create(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,

      setAuth: (data) => set({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        user: {
          id: data.user_id,
          role: data.role,
          fullName: data.full_name,
          isApproved: data.is_approved,
          preferredLanguage: data.preferred_language,
        },
        isAuthenticated: true,
      }),

      setToken: (token) => set({ accessToken: token }),

      logout: () => set({
        accessToken: null,
        refreshToken: null,
        user: null,
        isAuthenticated: false,
      }),

      updateUser: (updates) => set((state) => ({
        user: { ...state.user, ...updates }
      })),
    }),
    { name: 'auth-storage' }
  )
)

export default useAuthStore
