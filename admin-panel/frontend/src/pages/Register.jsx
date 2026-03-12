import { useState, useEffect } from 'react'
import { useNavigate, Link, useLocation } from 'react-router-dom'
import { authAPI } from '../api'
import { Briefcase, ArrowLeft } from 'lucide-react'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLegalEntity, setIsLegalEntity] = useState(false)
  const [companyName, setCompanyName] = useState('')
  const [inn, setInn] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (location.state?.message) {
      setSuccess(location.state.message)
    }
  }, [location])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Валидация
    if (!username || !email || !password || !confirmPassword) {
      setError('Все поля обязательны для заполнения')
      return
    }

    if (password !== confirmPassword) {
      setError('Пароли не совпадают')
      return
    }

    if (password.length < 6) {
      setError('Пароль должен содержать минимум 6 символов')
      return
    }

    // Проверка максимальной длины (72 байта - ограничение bcrypt)
    // Для ASCII символов это примерно 72 символа, для UTF-8 может быть меньше
    const passwordBytes = new TextEncoder().encode(password).length
    if (passwordBytes > 72) {
      setError('Пароль слишком длинный (максимум 72 байта, примерно 72 символа для ASCII)')
      return
    }

    // Валидация для юрлиц
    if (isLegalEntity) {
      if (!companyName || !companyName.trim()) {
        setError('Наименование компании обязательно для юридического лица')
        return
      }
      if (!inn || !inn.trim()) {
        setError('ИНН обязательно для юридического лица')
        return
      }
    }

    setLoading(true)

    try {
      await authAPI.register(username, email, password, isLegalEntity, companyName, inn)
      // После успешной регистрации перенаправляем на логин
      navigate('/login', { state: { message: 'Регистрация успешна! Войдите в систему.' } })
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Ошибка регистрации. Попробуйте еще раз.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
            <Briefcase className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Регистрация</h1>
          <p className="text-gray-600">Создание нового аккаунта администратора</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
              {success}
            </div>
          )}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Имя пользователя *
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
              placeholder="admin"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email *
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
              placeholder="admin@example.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Пароль *
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
              placeholder="••••••••"
            />
            <p className="mt-1 text-xs text-gray-500">Минимум 6 символов</p>
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
              Подтвердите пароль *
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Тип лица *
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="entityType"
                  checked={!isLegalEntity}
                  onChange={() => setIsLegalEntity(false)}
                  className="mr-2"
                />
                <span>Физическое лицо</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="entityType"
                  checked={isLegalEntity}
                  onChange={() => setIsLegalEntity(true)}
                  className="mr-2"
                />
                <span>Юридическое лицо</span>
              </label>
            </div>
          </div>

          {isLegalEntity && (
            <>
              <div>
                <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-2">
                  Наименование компании *
                </label>
                <input
                  id="companyName"
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  required={isLegalEntity}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                  placeholder="ООО 'Название компании'"
                />
              </div>

              <div>
                <label htmlFor="inn" className="block text-sm font-medium text-gray-700 mb-2">
                  ИНН *
                </label>
                <input
                  id="inn"
                  type="text"
                  value={inn}
                  onChange={(e) => setInn(e.target.value.replace(/\D/g, ''))}
                  required={isLegalEntity}
                  maxLength={12}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                  placeholder="1234567890"
                />
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <Link
            to="/login"
            className="inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Вернуться к входу</span>
          </Link>
        </div>
      </div>
    </div>
  )
}

