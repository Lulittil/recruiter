import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Users, Settings, Plus, Trash2, Edit } from 'lucide-react'
import { vacanciesAPI, applicantsAPI, managersAPI } from '../api'

export default function VacancyDetail() {
  const { id } = useParams()
  const [vacancy, setVacancy] = useState(null)
  const [applicants, setApplicants] = useState([])
  const [managers, setManagers] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('applicants')
  const [editingStrategy, setEditingStrategy] = useState(false)
  const [strategy, setStrategy] = useState('manual')
  const [maxCandidates, setMaxCandidates] = useState(null)

  useEffect(() => {
    loadData()
  }, [id])

  const loadData = async () => {
    try {
      const [vacancyData, managersData] = await Promise.all([
        vacanciesAPI.getById(id),
        managersAPI.getByVacancy(id),
      ])
      setVacancy(vacancyData)
      setStrategy(vacancyData.distribution_strategy || 'manual')
      setMaxCandidates(vacancyData.max_candidates_per_manager || null)
      const managers = managersData && managersData.managers ? managersData.managers : (Array.isArray(managersData) ? managersData : [])
      setManagers(Array.isArray(managers) ? managers : [])
      
      // Загружаем кандидатов
      try {
        const applicantsData = await applicantsAPI.getByVacancy(id)
        setApplicants(Array.isArray(applicantsData) ? applicantsData : [])
      } catch (error) {
        console.error('Error loading applicants:', error)
        setApplicants([])
      }
    } catch (error) {
      console.error('Error loading vacancy:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddManager = async () => {
    const chatId = prompt('Введите Telegram Chat ID менеджера:')
    if (chatId && !isNaN(chatId)) {
      try {
        await managersAPI.add(id, parseInt(chatId))
        loadData()
      } catch (error) {
        alert('Ошибка при добавлении менеджера')
      }
    }
  }

  const handleDeleteManager = async (managerId) => {
    if (confirm('Удалить менеджера из вакансии?')) {
      try {
        await managersAPI.delete(id, managerId)
        loadData()
      } catch (error) {
        alert('Ошибка при удалении менеджера')
      }
    }
  }

  const handleSaveStrategy = async () => {
    try {
      await vacanciesAPI.update(id, {
        distribution_strategy: strategy,
        max_candidates_per_manager: maxCandidates ? parseInt(maxCandidates) : null,
      })
      setEditingStrategy(false)
      loadData() // Перезагружаем данные
    } catch (error) {
      console.error('Error updating strategy:', error)
      alert('Ошибка при сохранении стратегии')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!vacancy) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Вакансия не найдена</p>
        <Link to="/vacancies" className="text-primary-600 hover:underline mt-4 inline-block">
          Вернуться к списку
        </Link>
      </div>
    )
  }

  return (
    <div>
      <Link
        to="/vacancies"
        className="inline-flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>Назад к вакансиям</span>
      </Link>

      <div className="bg-white rounded-lg shadow mb-6">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{vacancy.company_name}</h1>
              {vacancy.vacancy && (
                <p className="text-gray-600">{vacancy.vacancy}</p>
              )}
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              vacancy.is_closed
                ? 'bg-gray-100 text-gray-700'
                : 'bg-green-100 text-green-700'
            }`}>
              {vacancy.is_closed ? 'Закрыта' : 'Активна'}
            </span>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-600 mb-1">ID вакансии</p>
              <p className="font-mono font-semibold">{vacancy.vacancy_id}</p>
            </div>
            <div>
              <p className="text-gray-600 mb-1">Стратегия</p>
              <p className="font-semibold">{vacancy.distribution_strategy || 'manual'}</p>
            </div>
            <div>
              <p className="text-gray-600 mb-1">Макс. кандидатов</p>
              <p className="font-semibold">{vacancy.max_candidates_per_manager || '—'}</p>
            </div>
            <div>
              <p className="text-gray-600 mb-1">Анализов офферов</p>
              <p className="font-semibold">{vacancy.count_report_offers || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('applicants')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
                activeTab === 'applicants'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Users className="w-5 h-5 inline mr-2" />
              Кандидаты ({applicants.length})
            </button>
            <button
              onClick={() => setActiveTab('managers')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
                activeTab === 'managers'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Settings className="w-5 h-5 inline mr-2" />
              Менеджеры ({managers.length})
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition ${
                activeTab === 'settings'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Settings className="w-5 h-5 inline mr-2" />
              Настройки
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'applicants' && (
            <div>
              {applicants.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          ID
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Имя
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Telegram ID
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Телефон
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Статус
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {applicants.map((applicant) => (
                        <tr key={applicant.applicant_id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">
                            {applicant.applicant_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {applicant.full_name || '—'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {applicant.telegram_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {applicant.phone_number || '—'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                              {applicant.step_screen_id || 'Новый'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Кандидатов пока нет</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'managers' && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Менеджеры вакансии</h3>
                <button
                  onClick={handleAddManager}
                  className="inline-flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
                >
                  <Plus className="w-4 h-4" />
                  <span>Добавить менеджера</span>
                </button>
              </div>

              {managers.length > 0 ? (
                <div className="space-y-3">
                  {managers.map((manager) => (
                    <div
                      key={manager.vacancy_manager_id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition"
                    >
                      <div>
                        <p className="font-medium text-gray-900">
                          Chat ID: {manager.manager_chat_id}
                        </p>
                        <p className="text-sm text-gray-500">
                          Добавлен: {new Date(manager.created_at).toLocaleDateString('ru-RU')}
                        </p>
                      </div>
                      <button
                        onClick={() => handleDeleteManager(manager.vacancy_manager_id)}
                        className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded transition"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">Менеджеры не назначены</p>
                  <button
                    onClick={handleAddManager}
                    className="inline-flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Добавить менеджера</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'settings' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Настройки вакансии</h3>
              
              <div className="space-y-6">
                {/* Стратегия распределения */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Стратегия распределения кандидатов
                  </label>
                  {editingStrategy ? (
                    <div className="space-y-4">
                      <select
                        value={strategy}
                        onChange={(e) => setStrategy(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                      >
                        <option value="manual">Ручное (manual)</option>
                        <option value="round_robin">Round-robin (по кругу)</option>
                        <option value="least_loaded">Наименее загруженный (least_loaded)</option>
                        <option value="random">Случайное (random)</option>
                      </select>
                      
                      {(strategy === 'least_loaded' || strategy === 'round_robin') && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Максимум кандидатов на менеджера
                          </label>
                          <input
                            type="number"
                            value={maxCandidates || ''}
                            onChange={(e) => setMaxCandidates(e.target.value ? parseInt(e.target.value) : null)}
                            min="1"
                            placeholder="Не ограничено"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                          />
                        </div>
                      )}
                      
                      <div className="flex space-x-3">
                        <button
                          onClick={handleSaveStrategy}
                          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
                        >
                          Сохранить
                        </button>
                        <button
                          onClick={() => {
                            setEditingStrategy(false)
                            setStrategy(vacancy.distribution_strategy || 'manual')
                            setMaxCandidates(vacancy.max_candidates_per_manager || null)
                          }}
                          className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
                        >
                          Отмена
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">
                            {strategy === 'manual' ? 'Ручное' 
                             : strategy === 'round_robin' ? 'Round-robin'
                             : strategy === 'least_loaded' ? 'Наименее загруженный'
                             : 'Случайное'}
                          </p>
                          <p className="text-sm text-gray-600 mt-1">
                            {strategy === 'manual' 
                              ? 'Кандидаты назначаются вручную' 
                              : strategy === 'round_robin'
                              ? 'Кандидаты распределяются по кругу между менеджерами'
                              : strategy === 'least_loaded'
                              ? 'Кандидаты распределяются менеджерам с наименьшей загрузкой'
                              : 'Кандидаты распределяются случайным образом'}
                          </p>
                          {maxCandidates && (
                            <p className="text-sm text-gray-500 mt-1">
                              Максимум кандидатов на менеджера: {maxCandidates}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => setEditingStrategy(true)}
                          className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700 px-4 py-2 border border-primary-300 rounded-lg hover:bg-primary-50 transition"
                        >
                          <Edit className="w-4 h-4" />
                          <span>Изменить</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

