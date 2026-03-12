import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Briefcase, Users, TrendingUp, Plus } from 'lucide-react'
import { vacanciesAPI } from '../api'

export default function Dashboard() {
  const [vacancies, setVacancies] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    closed: 0,
    totalApplicants: 0,
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const data = await vacanciesAPI.getAll()
      // Убеждаемся, что data - массив
      const vacanciesArray = Array.isArray(data) ? data : []
      setVacancies(vacanciesArray)
      
      // Вычисляем статистику
      const active = vacanciesArray.filter(v => !v.is_closed).length
      const closed = vacanciesArray.filter(v => v.is_closed).length
      // TODO: Получить общее количество кандидатов
      setStats({
        total: vacanciesArray.length,
        active,
        closed,
        totalApplicants: 0,
      })
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      setVacancies([]) // Устанавливаем пустой массив при ошибке
    } finally {
      setLoading(false)
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Дашборд</h1>
        <p className="text-gray-600">Обзор системы RecruitR</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Всего вакансий</p>
              <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Briefcase className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Активные</p>
              <p className="text-3xl font-bold text-green-600">{stats.active}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Закрытые</p>
              <p className="text-3xl font-bold text-gray-600">{stats.closed}</p>
            </div>
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
              <Briefcase className="w-6 h-6 text-gray-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Кандидатов</p>
              <p className="text-3xl font-bold text-purple-600">{stats.totalApplicants}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Vacancies */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">Последние вакансии</h2>
          <Link
            to="/vacancies"
            className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 font-medium"
          >
            <span>Все вакансии</span>
          </Link>
        </div>
        <div className="divide-y">
          {Array.isArray(vacancies) && vacancies.slice(0, 5).map((vacancy) => (
            <Link
              key={vacancy.vacancy_id}
              to={`/vacancies/${vacancy.vacancy_id}`}
              className="block p-6 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {vacancy.company_name}
                  </h3>
                  {vacancy.vacancy && (
                    <p className="text-sm text-gray-600 mb-2">{vacancy.vacancy}</p>
                  )}
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      vacancy.is_closed
                        ? 'bg-gray-100 text-gray-700'
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {vacancy.is_closed ? 'Закрыта' : 'Активна'}
                    </span>
                    <span>
                      Стратегия: {vacancy.distribution_strategy || 'manual'}
                    </span>
                  </div>
                </div>
                <Briefcase className="w-5 h-5 text-gray-400" />
              </div>
            </Link>
          ))}
          {vacancies.length === 0 && (
            <div className="p-12 text-center">
              <Briefcase className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">Вакансии отсутствуют</p>
              <Link
                to="/vacancies"
                className="inline-flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
              >
                <Plus className="w-4 h-4" />
                <span>Создать вакансию</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

