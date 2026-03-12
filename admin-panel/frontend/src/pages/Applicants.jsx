import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Users, Briefcase, Calendar, Phone, User } from 'lucide-react'
import { applicantsAPI } from '../api'
import { vacanciesAPI } from '../api'

export default function Applicants() {
  const [applicants, setApplicants] = useState([])
  const [vacancies, setVacancies] = useState([])
  const [loading, setLoading] = useState(true)
  const [vacanciesMap, setVacanciesMap] = useState({})

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [applicantsData, vacanciesData] = await Promise.all([
        applicantsAPI.getAll(),
        vacanciesAPI.getAll()
      ])
      
      setApplicants(Array.isArray(applicantsData) ? applicantsData : [])
      const vacanciesList = Array.isArray(vacanciesData) ? vacanciesData : []
      setVacancies(vacanciesList)
      
      // Создаем карту вакансий для быстрого доступа
      const map = {}
      vacanciesList.forEach(v => {
        map[v.vacancy_id] = v
      })
      setVacanciesMap(map)
    } catch (error) {
      console.error('Error loading applicants:', error)
      setApplicants([])
      setVacancies([])
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Не указано'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Кандидаты</h1>
        <p className="text-gray-600">Все кандидаты по вакансиям</p>
      </div>

      {applicants.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Кандидаты отсутствуют</h3>
          <p className="text-gray-600">Пока нет кандидатов по вашим вакансиям</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Кандидат
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Вакансия
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Контакты
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Дата отклика
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Статус
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {applicants.map((applicant) => {
                  const vacancy = vacanciesMap[applicant.vacancy_id]
                  return (
                    <tr key={applicant.applicant_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center mr-3">
                            <User className="w-5 h-5 text-primary-600" />
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {applicant.full_name || `ID: ${applicant.telegram_id}`}
                            </div>
                            <div className="text-sm text-gray-500">
                              Telegram ID: {applicant.telegram_id}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {vacancy ? (
                          <Link
                            to={`/vacancies/${vacancy.vacancy_id}`}
                            className="inline-flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-800"
                          >
                            <Briefcase className="w-4 h-4" />
                            <span className="font-medium">{vacancy.company_name}</span>
                          </Link>
                        ) : (
                          <span className="text-sm text-gray-500">Вакансия удалена</span>
                        )}
                        {vacancy && vacancy.vacancy && (
                          <div className="text-xs text-gray-500 mt-1 truncate max-w-xs">
                            {vacancy.vacancy}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {applicant.phone_number ? (
                          <div className="flex items-center text-sm text-gray-900">
                            <Phone className="w-4 h-4 mr-1 text-gray-400" />
                            {applicant.phone_number}
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400">Не указан</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-500">
                          <Calendar className="w-4 h-4 mr-1 text-gray-400" />
                          {formatDate(applicant.date_consent)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          applicant.is_sended
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {applicant.is_sended ? 'Отправлен' : 'Новый'}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

