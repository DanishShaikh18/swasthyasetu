import client from './client'

export const register = (data) => client.post('/api/v1/auth/register', data)
export const login = (data) => client.post('/api/v1/auth/login', data)
export const logout = () => client.post('/api/v1/auth/logout')
export const refresh = () => client.post('/api/v1/auth/refresh')
