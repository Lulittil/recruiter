import { Link, useLocation } from 'react-router-dom'
import { Home, Briefcase, LogOut, User, Users, CreditCard } from 'lucide-react'
import { useState, useEffect } from 'react'
import { authAPI } from '../api'

export default function Layout({ children, onLogout }) {
  const location = useLocation()
  const [userInfo, setUserInfo] = useState({ username: 'Admin', email: '' })

  useEffect(() => {
    // Загружаем информацию о текущем пользователе
    authAPI.getMe()
      .then(data => {
        setUserInfo({
          username: data.username || 'Admin',
          email: data.email || ''
        })
      })
      .catch(error => {
        console.error('Error loading user info:', error)
      })
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    onLogout()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b">
            <h1 className="text-2xl font-bold text-primary-600">RecruitR</h1>
            <p className="text-sm text-gray-500">Admin Panel</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            <Link
              to="/"
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname === '/'
                  ? 'bg-primary-50 text-primary-600 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Home className="w-5 h-5" />
              <span>Дашборд</span>
            </Link>
            <Link
              to="/vacancies"
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname.startsWith('/vacancies') && !location.pathname.startsWith('/applicants')
                  ? 'bg-primary-50 text-primary-600 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Briefcase className="w-5 h-5" />
              <span>Вакансии</span>
            </Link>
            <Link
              to="/applicants"
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname.startsWith('/applicants')
                  ? 'bg-primary-50 text-primary-600 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Users className="w-5 h-5" />
              <span>Кандидаты</span>
            </Link>
            <Link
              to="/managers"
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname.startsWith('/managers')
                  ? 'bg-primary-50 text-primary-600 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <User className="w-5 h-5" />
              <span>Менеджеры</span>
            </Link>
            <Link
              to="/payment"
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                location.pathname.startsWith('/payment')
                  ? 'bg-primary-50 text-primary-600 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <CreditCard className="w-5 h-5" />
              <span>Оплата</span>
            </Link>
          </nav>

          {/* User info */}
          <div className="p-4 border-t">
            <div className="flex items-center space-x-3 px-4 py-2">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                <User className="w-5 h-5 text-primary-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{userInfo.username}</p>
                <p className="text-xs text-gray-500">{userInfo.email || 'Администратор'}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center space-x-3 px-4 py-2 mt-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span>Выход</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-64 p-8">
        {children}
      </main>
    </div>
  )
}

