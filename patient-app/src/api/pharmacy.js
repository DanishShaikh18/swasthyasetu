import client from './client'
export const searchPharmacy = (params) => client.get('/api/v1/pharmacy/search', { params })
