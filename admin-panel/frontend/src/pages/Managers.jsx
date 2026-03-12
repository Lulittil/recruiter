import { useEffect, useState } from 'react'
import { Plus, Edit, Trash2, User, Search, Key } from 'lucide-react'
import { managersAPI, vacanciesAPI } from '../api'

export default function Managers() {
  const [managers, setManagers] = useState([])
  const [vacancies, setVacancies] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [selectedManager, setSelectedManager] = useState(null)
  const [formData, setFormData] = useState({
    vacancy_id: '',
    manager_chat_id: '',
    full_name: '',
    email: '',
    password: '',
  })
  const [passwordForm, setPasswordForm] = useState({
    password: '',
    confirmPassword: '',
  })

  useEffect(() => {
    loadManagers()
    loadVacancies()
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => {
      loadManagers(searchQuery)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchQuery])

  const loadManagers = async (search = '') => {
    try {
      setLoading(true)
      const data = await managersAPI.getAll()
      let filtered = Array.isArray(data) ? data : []
      
      if (search) {
        filtered = filtered.filter(m => 
          (m.full_name && m.full_name.toLowerCase().includes(search.toLowerCase())) ||
          (m.email && m.email.toLowerCase().includes(search.toLowerCase())) ||
          String(m.manager_chat_id).includes(search)
        )
      }
      
      setManagers(filtered)
    } catch (error) {
      console.error('Error loading managers:', error)
      setManagers([])
    } finally {
      setLoading(false)
    }
  }

  const loadVacancies = async () => {
    try {
      const data = await vacanciesAPI.getAll()
      setVacancies(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error loading vacancies:', error)
      setVacancies([])
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      if (!formData.vacancy_id || !formData.manager_chat_id || !formData.email || !formData.password) {
        alert('Заполните все обязательные поля')
        return
      }

      await managersAPI.create({
        vacancy_id: parseInt(formData.vacancy_id),
        manager_chat_id: parseInt(formData.manager_chat_id),
        full_name: formData.full_name || null,
        email: formData.email,
        password: formData.password,
      })
      
      setShowCreateModal(false)
      setFormData({
        vacancy_id: '',
        manager_chat_id: '',
        full_name: '',
        email: '',
        password: '',
      })
      loadManagers(searchQuery)
    } catch (error) {
      console.error('Error creating manager:', error)
      alert(`Ошибка при создании менеджера: ${error.response?.data?.detail || error.message}`)
    }
  }

  const handleUpdatePassword = async (e) => {
    e.preventDefault()
    try {
      if (passwordForm.password !== passwordForm.confirmPassword) {
        alert('Пароли не совпадают')
        return
      }

      if (passwordForm.password.length < 6) {
        alert('Пароль должен быть не менее 6 символов')
        return
      }

      await managersAPI.updatePassword(selectedManager.vacancy_manager_id, passwordForm.password)
      
      setShowPasswordModal(false)
      setSelectedManager(null)
      setPasswordForm({ password: '', confirmPassword: '' })
      alert('Пароль успешно обновлен')
    } catch (error) {
      console.error('Error updating password:', error)
      alert(`Ошибка при обновлении пароля: ${error.response?.data?.detail || error.message}`)
    }
  }

  const openPasswordModal = (manager) => {
    setSelectedManager(manager)
    setPasswordForm({ password: '', confirmPassword: '' })
    setShowPasswordModal(true)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Менеджеры</h1>
          <p className="text-gray-600">Управление менеджерами и их паролями</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
        >
          <Plus className="w-5 h-5" />
          <span>Добавить менеджера</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Поиск по ФИО, email или ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Managers Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ФИО
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Email
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID менеджера
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID вакансии
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {managers.map((manager) => (
              <tr key={manager.vacancy_manager_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {manager.full_name || 'Не указано'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{manager.email || 'Не указано'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900 font-mono">{manager.manager_chat_id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900 font-mono">{manager.vacancy_id}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => openPasswordModal(manager)}
                    className="text-primary-600 hover:text-primary-900 flex items-center space-x-1"
                  >
                    <Key className="w-4 h-4" />
                    <span>Изменить пароль</span>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {managers.length === 0 && (
          <div className="p-12 text-center">
            <User className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Менеджеры отсутствуют</h3>
            <p className="text-gray-600 mb-6">Создайте первого менеджера для начала работы</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition"
            >
              <Plus className="w-5 h-5" />
              <span>Добавить менеджера</span>
            </button>
          </div>
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold text-gray-900">Добавить менеджера</h2>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Вакансия *
                </label>
                <select
                  required
                  value={formData.vacancy_id}
                  onChange={(e) => setFormData({ ...formData, vacancy_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Выберите вакансию</option>
                  {vacancies.map((v) => (
                    <option key={v.vacancy_id} value={v.vacancy_id}>
                      {v.company_name} (ID: {v.vacancy_id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  ФИО
                </label>
                <input
                  type="text"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Иванов Иван Иванович"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Логин (ID менеджера в Telegram) *
                </label>
                <input
                  type="number"
                  required
                  value={formData.manager_chat_id}
                  onChange={(e) => setFormData({ ...formData, manager_chat_id: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono"
                  placeholder="123456789"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="manager@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Пароль *
                </label>
                <input
                  type="password"
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Минимум 6 символов"
                  minLength={6}
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                >
                  Создать
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Password Update Modal */}
      {showPasswordModal && selectedManager && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold text-gray-900">Изменить пароль</h2>
              <p className="text-sm text-gray-600 mt-1">
                Менеджер: {selectedManager.full_name || selectedManager.email || `ID: ${selectedManager.manager_chat_id}`}
              </p>
            </div>
            <form onSubmit={handleUpdatePassword} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Новый пароль *
                </label>
                <input
                  type="password"
                  required
                  value={passwordForm.password}
                  onChange={(e) => setPasswordForm({ ...passwordForm, password: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Минимум 6 символов"
                  minLength={6}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Подтвердите пароль *
                </label>
                <input
                  type="password"
                  required
                  value={passwordForm.confirmPassword}
                  onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Повторите пароль"
                  minLength={6}
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordModal(false)
                    setSelectedManager(null)
                    setPasswordForm({ password: '', confirmPassword: '' })
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                >
                  Сохранить
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

