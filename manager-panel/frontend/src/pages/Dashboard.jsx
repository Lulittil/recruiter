import { Link } from 'react-router-dom'
import { Users, Calendar } from 'lucide-react'

export default function Dashboard() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Панель управления</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link
          to="/candidates"
          className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow border border-gray-200"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Кандидаты</h2>
              <p className="text-gray-500 text-sm">Управление кандидатами</p>
            </div>
          </div>
        </Link>

        <Link
          to="/calendar"
          className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow border border-gray-200"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Календарь</h2>
              <p className="text-gray-500 text-sm">Управление созвонами</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  )
}

