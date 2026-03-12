import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, User, Phone, Briefcase, Calendar, FileText, ClipboardList } from 'lucide-react'
import { candidatesAPI } from '../api'
import { format } from 'date-fns'
import ru from 'date-fns/locale/ru'

export default function CandidateDetail() {
  const { id } = useParams()
  const [candidate, setCandidate] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCandidate()
  }, [id])

  const loadCandidate = async () => {
    try {
      const data = await candidatesAPI.getById(id)
      setCandidate(data)
    } catch (error) {
      console.error('Error loading candidate:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Не указано'
    try {
      return format(new Date(dateString), 'dd.MM.yyyy HH:mm', { locale: ru })
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

  if (!candidate) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Кандидат не найден</p>
        <Link to="/candidates" className="text-primary-600 hover:underline mt-4 inline-block">
          Вернуться к списку
        </Link>
      </div>
    )
  }

  return (
    <div>
      <Link
        to="/candidates"
        className="inline-flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>Назад к кандидатам</span>
      </Link>

      <div className="bg-white rounded-lg shadow mb-6">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {candidate.full_name || `Кандидат #${candidate.applicant_id}`}
              </h1>
              {candidate.vacancy_name && (
                <p className="text-gray-600">{candidate.vacancy_name}</p>
              )}
            </div>
            {candidate.step_screen_name && (
              <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                {candidate.step_screen_name}
              </span>
            )}
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Контакты</h2>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <User className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Telegram ID</p>
                    <p className="font-mono">{candidate.telegram_id}</p>
                  </div>
                </div>
                {candidate.phone_number && (
                  <div className="flex items-center space-x-3">
                    <Phone className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">Телефон</p>
                      <p>{candidate.phone_number}</p>
                    </div>
                  </div>
                )}
                {candidate.date_consent && (
                  <div className="flex items-center space-x-3">
                    <Calendar className="w-5 h-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">Дата согласия</p>
                      <p>{formatDate(candidate.date_consent)}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Информация</h2>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Briefcase className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Вакансия ID</p>
                    <p>{candidate.vacancy_id || 'Не указано'}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <ClipboardList className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Статус</p>
                    <p>{candidate.step_screen_name || 'Не указан'}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {candidate.resume && (
            <div className="mt-6 pt-6 border-t">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <FileText className="w-5 h-5" />
                <span>Резюме</span>
              </h2>
              <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                  {candidate.resume}
                </pre>
              </div>
            </div>
          )}

          {candidate.primary_analysis && (
            <div className="mt-6 pt-6 border-t">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Анализ после первичного скрининга</h2>
              <div className="bg-blue-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                <div className="text-sm text-gray-700 whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: candidate.primary_analysis }} />
              </div>
            </div>
          )}

          {candidate.second_analysis && (
            <div className="mt-6 pt-6 border-t">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Анализ после второго скрининга</h2>
              <div className="bg-purple-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                <div className="text-sm text-gray-700 whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: candidate.second_analysis }} />
              </div>
            </div>
          )}

          {!candidate.primary_analysis && !candidate.second_analysis && !candidate.resume && (
            <div className="mt-6 pt-6 border-t text-center text-gray-500">
              <p>Дополнительная информация отсутствует</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

