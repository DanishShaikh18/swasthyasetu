import client from './client'

export const checkSymptoms = (data) => client.post('/api/v1/ai/symptoms', data)
export const getDailyTip = (params) => client.get('/api/v1/content/daily-tip', { params })
export const getFirstAid = (params) => client.get('/api/v1/content/first-aid', { params })
export const getHealthFacts = (params) => client.get('/api/v1/content/health-facts', { params })
export const getNotifications = (params) => client.get('/api/v1/content/notifications/me', { params })
