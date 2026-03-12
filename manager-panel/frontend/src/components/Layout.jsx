import { useState, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { Users, Calendar, LogOut, Menu, X, Settings } from 'lucide-react'
import { managerAPI } from '../api'

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [managerEmail, setManagerEmail] = useState('')
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const fetchManagerInfo = async () => {
      try {
        const info = await managerAPI.getMe()
        setManagerEmail(info.email || '')
      } catch (error) {
        console.error('Error fetching manager info:', error)
      }
    }
    fetchManagerInfo()
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  const menuItems = [
    { path: '/', icon: Users, label: 'Кандидаты' },
    { path: '/calendar', icon: Calendar, label: 'Календарь' },
    { path: '/calendar/settings', icon: Settings, label: 'Настройки календаря' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full bg-white border-r border-gray-200 transition-transform duration-300 z-30 ${
          sidebarOpen ? 'translate-x-0 w-64' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          <div className="p-6 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-primary-600">RecruitR</h1>
            <p className="text-sm text-gray-500 mt-1">Менеджерская панель</p>
          </div>

          <nav className="flex-1 p-4 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-600'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              )
            })}
          </nav>

          <div className="p-4 border-t border-gray-200">
            <div className="mb-4">
              <p className="text-sm text-gray-500">Вошли как:</p>
              <p className="text-sm font-medium text-gray-900 truncate">{managerEmail}</p>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center space-x-3 px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Выйти</span>
            </button>
          </div>
        </div>
      </div>

      {/* Overlay для мобильных */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className={`transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : 'ml-0'}`}>
        {/* Top bar */}
        <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center justify-between sticky top-0 z-10">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
          <div className="flex-1" />
        </div>

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}

