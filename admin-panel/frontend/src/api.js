import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем токен к каждому запросу
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
  login: async (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    const response = await axios.post(`${API_URL}/auth/login`, formData)
    return response.data
  },
  register: async (username, email, password, isLegalEntity = false, companyName = null, inn = null) => {
    const response = await api.post('/auth/register', {
      username,
      email,
      password,
      is_legal_entity: isLegalEntity,
      company_name: companyName,
      inn: inn,
    })
    return response.data
  },
  getMe: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },
}

export const vacanciesAPI = {
  getAll: async (search = '') => {
    const params = search ? { search } : {}
    const response = await api.get('/vacancies', { params })
    return Array.isArray(response.data) ? response.data : []
  },
  getById: async (id) => {
    const response = await api.get(`/vacancies/${id}`)
    return response.data
  },
  create: async (data) => {
    const response = await api.post('/vacancies', data)
    return response.data
  },
  update: async (id, data) => {
    const response = await api.put(`/vacancies/${id}`, data)
    return response.data
  },
  getStats: async (id) => {
    const response = await api.get(`/vacancies/${id}/stats`)
    return response.data
  },
}

export const applicantsAPI = {
  getAll: async () => {
    const response = await api.get('/applicants')
    return Array.isArray(response.data) ? response.data : []
  },
  getByVacancy: async (vacancyId) => {
    const response = await api.get(`/vacancies/${vacancyId}/applicants`)
    return Array.isArray(response.data) ? response.data : []
  },
  getById: async (telegramId) => {
    const response = await api.get(`/applicants/${telegramId}`)
    return response.data
  },
  update: async (telegramId, data) => {
    const response = await api.patch(`/applicants/${telegramId}`, data)
    return response.data
  },
}

export const managersAPI = {
  getAll: async () => {
    const response = await api.get('/managers/all')
    return Array.isArray(response.data) ? response.data : []
  },
  getByVacancy: async (vacancyId) => {
    const response = await api.get(`/vacancies/${vacancyId}/managers`)
    // Может возвращаться как массив или как объект с полем managers
    if (response.data.managers) {
      return response.data
    }
    return { managers: Array.isArray(response.data) ? response.data : [] }
  },
  create: async (data) => {
    const response = await api.post('/managers', data)
    return response.data
  },
  updatePassword: async (managerId, password) => {
    const response = await api.put(`/managers/${managerId}/password`, { password })
    return response.data
  },
  add: async (vacancyId, managerChatId) => {
    const response = await api.post(`/vacancies/${vacancyId}/managers`, {
      manager_chat_id: managerChatId,
    })
    return response.data
  },
  delete: async (vacancyId, managerId) => {
    const response = await api.delete(`/vacancies/${vacancyId}/managers/${managerId}`)
    return response.data
  },
}

export const stepsAPI = {
  getAll: () => api.get('/steps'),
}

export const paymentsAPI = {
  getTariffs: async () => {
    const response = await api.get('/tariffs')
    return Array.isArray(response.data) ? response.data : []
  },
  create: async (tariffId, paymentType, companyName = null, inn = null, kpp = null, legalAddress = null, email = null) => {
    const payload = {
      tariff_id: tariffId,
      payment_type: paymentType,
    }
    if (companyName) payload.company_name = companyName
    if (inn) payload.inn = inn
    if (kpp) payload.kpp = kpp
    if (legalAddress) payload.legal_address = legalAddress
    if (email) payload.email = email
    
    const response = await api.post('/payments/create', payload)
    return response.data
  },
}

export default api

