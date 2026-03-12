import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем токен к запросам
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Обработка ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }).then(res => res.data),
}

export const managerAPI = {
  getMe: () => api.get('/me').then(res => res.data),
}

export const candidatesAPI = {
  getAll: () => api.get('/candidates').then(res => res.data),
  getById: (id) => api.get(`/candidates/${id}`).then(res => res.data),
}

export const calendarAPI = {
  getEvents: (startDate, endDate) => {
    const params = {}
    if (startDate) params.start_date = startDate.toISOString()
    if (endDate) params.end_date = endDate.toISOString()
    return api.get('/calendar/events', { params }).then(res => res.data)
  },
  createEvent: (event) => api.post('/calendar/events', event).then(res => res.data),
  updateEvent: (id, event) => api.put(`/calendar/events/${id}`, event).then(res => res.data),
  deleteEvent: (id) => api.delete(`/calendar/events/${id}`).then(res => res.data),
  getEvent: (id) => api.get(`/calendar/events/${id}`).then(res => res.data),
  getSettings: () => api.get('/calendar/settings').then(res => res.data),
  updateSettings: (settings) => api.put('/calendar/settings', settings).then(res => res.data),
}

export default api

