import client from './client'

export const listDoctors = (params) => client.get('/api/v1/doctors', { params })
export const getDoctorSlots = (doctorId, params) => client.get(`/api/v1/doctors/${doctorId}/slots`, { params })
export const joinVideoCall = (appointmentId) => client.get(`/api/v1/appointments/${appointmentId}/join`)
