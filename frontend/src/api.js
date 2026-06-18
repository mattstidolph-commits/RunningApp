import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getDashboard = () => api.get('/dashboard').then(r => r.data)
export const getActivities = () => api.get('/activities').then(r => r.data)
export const uploadFit = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/activities/upload-fit', form).then(r => r.data)
}
export const getPlans = () => api.get('/plans').then(r => r.data)
export const activatePlan = (planId, startDate) =>
  api.post(`/plans/${planId}/activate`, { start_date: startDate }).then(r => r.data)
export const getWorkouts = () => api.get('/plans/workouts').then(r => r.data)
export const updateWorkout = (id, data) =>
  api.put(`/plans/workouts/${id}`, data).then(r => r.data)
export const getMobilityRoutines = (area) =>
  api.get('/mobility/routines', { params: area ? { area } : {} }).then(r => r.data)
export const getMobilityRecommendation = () =>
  api.get('/mobility/recommendation').then(r => r.data)
export const logMobilitySession = (data) =>
  api.post('/mobility/sessions', data).then(r => r.data)
export const getMobilitySessions = (days = 30) =>
  api.get('/mobility/sessions', { params: { days } }).then(r => r.data)
export const getProgressCharts = () => api.get('/progress/charts').then(r => r.data)
export const syncGarmin = () => api.post('/garmin/sync').then(r => r.data)
