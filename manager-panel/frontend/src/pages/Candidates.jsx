import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { User, Phone, Briefcase, Calendar, FileText } from 'lucide-react'
import { candidatesAPI } from '../api'
import { format } from 'date-fns'
import ru from 'date-fns/locale/ru'

export default function Candidates() {
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCandidates()
  }, [])

  const loadCandidates = async () => {
    try {
      const data = await candidatesAPI.getAll()
      setCandidates(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Error loading candidates:', error)
      setCandidates([])
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

  const getStatusBadge = (stepName) => {
    if (!stepName) return <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">Не указан</span>
    
    const statusColors = {
      'получен отчет': 'bg-blue-100 text-blue-700',
      'приглашен на второй этап': 'bg-green-100 text-green-700',
      'отказ после первого этапа': 'bg-red-100 text-red-700',
      'прошел второй этап': 'bg-purple-100 text-purple-700',
      'отказ после второго этапа': 'bg-red-100 text-red-700',
    }
    
    const colorClass = statusColors[stepName.toLowerCase()] || 'bg-gray-100 text-gray-700'
    return <span className={`px-2 py-1 rounded text-xs ${colorClass}`}>{stepName}</span>
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
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Кандидаты</h1>
      </div>

      {candidates.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <User className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Кандидаты не найдены</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {candidates.map((candidate) => (
            <Link
              key={candidate.applicant_id}
              to={`/candidates/${candidate.applicant_id}`}
              className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow border border-gray-200"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {candidate.full_name || `Кандидат #${candidate.applicant_id}`}
                    </h3>
                    {getStatusBadge(candidate.step_screen_name)}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                    {candidate.vacancy_name && (
                      <div className="flex items-center space-x-2">
                        <Briefcase className="w-4 h-4" />
                        <span>{candidate.vacancy_name}</span>
                      </div>
                    )}
                    {candidate.phone_number && (
                      <div className="flex items-center space-x-2">
                        <Phone className="w-4 h-4" />
                        <span>{candidate.phone_number}</span>
                      </div>
                    )}
                    {candidate.date_consent && (
                      <div className="flex items-center space-x-2">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(candidate.date_consent)}</span>
                      </div>
                    )}
                  </div>

                  {candidate.resume && (
                    <div className="mt-3 flex items-center space-x-2 text-sm text-gray-500">
                      <FileText className="w-4 h-4" />
                      <span>Резюме загружено</span>
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

