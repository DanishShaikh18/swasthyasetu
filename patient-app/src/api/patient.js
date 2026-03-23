import client from './client'

export const getProfile = () => client.get('/api/v1/patients/me')
export const updateProfile = (data) => client.patch('/api/v1/patients/me', data)
export const getPrescriptions = (params) => client.get('/api/v1/patients/me/prescriptions', { params })
export const getAppointments = (params) => client.get('/api/v1/patients/me/appointments', { params })
export const bookAppointment = (data) => client.post('/api/v1/patients/appointments', data)
export const getDocuments = () => client.get('/api/v1/patients/me/documents')
export const uploadDocument = (data) => client.post('/api/v1/patients/me/documents', data)
