import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Edit, Trash2, Briefcase, Search } from 'lucide-react'
import { vacanciesAPI } from '../api'

export default function Vacancies() {
  const [vacancies, setVacancies] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [formData, setFormData] = useState({
    company_name: '',
    bot_token: '',
    vacancy: '',
    is_closed: false,
    distribution_strategy: 'manual',
    max_candidates_per_manager: null,
  })

  useEffect(() => {
    loadVacancies('')
  }, [])

  useEffect(() => {
    // Загружаем вакансии при изменении поискового запроса с задержкой (debounce)
    const timer = setTimeout(() => {
      loadVacancies(searchQuery)
    }, 300) // Задержка 300ms для debounce

    return () => clearTimeout(timer)
  }, [searchQuery])

  const loadVacancies = async (search = '') => {
    try {
      setLoading(true)
      const data = await vacanciesAPI.getAll(search)
      setVacancies(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error loading vacancies:', error)
      setVacancies([]) // Устанавливаем пустой массив при ошибке
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      // Преобразуем пустые строки в null и очищаем данные перед отправкой
      const dataToSend = {
        company_name: formData.company_name || '',
        bot_token: formData.bot_token || '',
        vacancy: formData.vacancy || null,
        is_closed: formData.is_closed || false,
        distribution_strategy: formData.distribution_strategy || 'manual',
        max_candidates_per_manager: formData.max_candidates_per_manager || null,
      }
      
      console.log('Sending vacancy data:', dataToSend)
      await vacanciesAPI.create(dataToSend)
      setShowCreateModal(false)
      setFormData({
        company_name: '',
        bot_token: '',
        vacancy: '',
        is_closed: false,
        distribution_strategy: 'manual',
        max_candidates_per_manager: null,
      })
      loadVacancies(searchQuery)
    } catch (error) {
      console.error('Error creating vacancy:', error)
      console.error('Error response:', error.response?.data)
      alert(`Ошибка при создании вакансии: ${error.response?.data?.detail || error.message}`)
    }
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Вакансии</h1>
          <p className="text-gray-600">Управление вакансиями и настройками ботов</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
        >
          <Plus className="w-5 h-5" />
          <span>Создать вакансию</span>
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Поиск по названию компании или вакансии..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Vacancies Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {vacancies.map((vacancy) => (
          <div key={vacancy.vacancy_id} className="bg-white rounded-lg shadow hover:shadow-lg transition">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {vacancy.company_name}
                  </h3>
                  {vacancy.vacancy && (
                    <p className="text-sm text-gray-600 line-clamp-2">{vacancy.vacancy}</p>
                  )}
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  vacancy.is_closed
                    ? 'bg-gray-100 text-gray-700'
                    : 'bg-green-100 text-green-700'
                }`}>
                  {vacancy.is_closed ? 'Закрыта' : 'Активна'}
                </span>
              </div>

              <div className="space-y-2 mb-4 text-sm text-gray-600">
                <div className="flex items-center justify-between">
                  <span>ID:</span>
                  <span className="font-mono">{vacancy.vacancy_id}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Стратегия:</span>
                  <span>{vacancy.distribution_strategy || 'manual'}</span>
                </div>
                {vacancy.max_candidates_per_manager && (
                  <div className="flex items-center justify-between">
                    <span>Макс. кандидатов:</span>
                    <span>{vacancy.max_candidates_per_manager}</span>
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-2 pt-4 border-t">
                <Link
                  to={`/vacancies/${vacancy.vacancy_id}`}
                  className="flex-1 bg-primary-50 text-primary-600 px-4 py-2 rounded-lg text-center hover:bg-primary-100 transition font-medium"
                >
                  Открыть
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>

      {vacancies.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Briefcase className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Вакансии отсутствуют</h3>
          <p className="text-gray-600 mb-6">Создайте первую вакансию для начала работы</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition"
          >
            <Plus className="w-5 h-5" />
            <span>Создать вакансию</span>
          </button>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-2xl font-bold text-gray-900">Создать вакансию</h2>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Название компании *
                </label>
                <input
                  type="text"
                  required
                  value={formData.company_name}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Токен бота Telegram *
                </label>
                <input
                  type="text"
                  required
                  value={formData.bot_token}
                  onChange={(e) => setFormData({ ...formData, bot_token: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
                  placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Описание вакансии
                </label>
                <textarea
                  value={formData.vacancy}
                  onChange={(e) => setFormData({ ...formData, vacancy: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Стратегия распределения
                  </label>
                  <select
                    value={formData.distribution_strategy}
                    onChange={(e) => setFormData({ ...formData, distribution_strategy: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="manual">Ручное</option>
                    <option value="round_robin">Round Robin</option>
                    <option value="least_loaded">Наименее загруженный</option>
                    <option value="random">Случайное</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Макс. кандидатов на менеджера
                  </label>
                  <input
                    type="number"
                    value={formData.max_candidates_per_manager || ''}
                    onChange={(e) => setFormData({ 
                      ...formData, 
                      max_candidates_per_manager: e.target.value ? parseInt(e.target.value) : null 
                    })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-4 border-t">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.is_closed}
                    onChange={(e) => setFormData({ ...formData, is_closed: e.target.checked })}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">Вакансия закрыта</span>
                </label>
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
    </div>
  )
}

