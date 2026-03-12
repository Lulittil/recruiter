import { useState, useEffect } from 'react'
import { CreditCard, Building2, User, AlertCircle, CheckCircle, Package, Sparkles } from 'lucide-react'
import { paymentsAPI, authAPI } from '../api'

export default function Payment() {
  const [tariffs, setTariffs] = useState([])
  const [selectedTariff, setSelectedTariff] = useState(null)
  const [paymentType, setPaymentType] = useState('individual') // 'individual' or 'legal_entity'
  const [companyName, setCompanyName] = useState('')
  const [inn, setInn] = useState('')
  const [kpp, setKpp] = useState('')
  const [legalAddress, setLegalAddress] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingTariffs, setLoadingTariffs] = useState(true)
  const [error, setError] = useState('')
  const [paymentUrl, setPaymentUrl] = useState('')
  const [userInfo, setUserInfo] = useState(null)

  useEffect(() => {
    // Загружаем тарифы
    paymentsAPI.getTariffs()
      .then(data => {
        setTariffs(data)
      })
      .catch(error => {
        console.error('Error loading tariffs:', error)
        setError('Ошибка при загрузке тарифов')
      })
      .finally(() => {
        setLoadingTariffs(false)
      })

    // Загружаем информацию о текущем пользователе
    authAPI.getMe()
      .then(data => {
        setUserInfo(data)
        if (data.is_legal_entity) {
          setPaymentType('legal_entity')
          if (data.company_name) setCompanyName(data.company_name)
          if (data.inn) setInn(data.inn)
        }
      })
      .catch(error => {
        console.error('Error loading user info:', error)
      })
  }, [])

  const handleTariffSelect = (tariff) => {
    setSelectedTariff(tariff)
    setPaymentUrl('')
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setPaymentUrl('')

    if (!selectedTariff) {
      setError('Выберите тариф')
      return
    }

    if (paymentType === 'legal_entity') {
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
      const result = await paymentsAPI.create(
        selectedTariff.id,
        paymentType,
        companyName || null,
        inn || null,
        kpp || null,
        legalAddress || null,
        email || null
      )

      if (result.payment_url) {
        setPaymentUrl(result.payment_url)
      } else {
        setError('Не удалось получить ссылку на оплату. Попробуйте еще раз.')
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Ошибка при создании платежа')
    } finally {
      setLoading(false)
    }
  }

  if (loadingTariffs) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Оплата тарифа</h1>
        <p className="text-gray-600">Выберите тариф и создайте платеж</p>
      </div>

      {!selectedTariff ? (
        /* Выбор тарифа */
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {tariffs.map((tariff) => (
            <div
              key={tariff.id}
              onClick={() => handleTariffSelect(tariff)}
              className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow border-2 border-transparent hover:border-primary-500"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Package className="w-6 h-6 text-primary-600" />
                  <h3 className="text-xl font-bold text-gray-900">{tariff.name}</h3>
                </div>
              </div>
              
              <p className="text-gray-600 text-sm mb-4">{tariff.description}</p>
              
              <div className="space-y-2 mb-4">
                <div className="flex items-center text-gray-700">
                  <span className="text-sm">📋 Вакансий: <strong>{tariff.vacancies_count}</strong></span>
                </div>
                <div className="flex items-center text-gray-700">
                  <span className="text-sm">🔍 Анализов офферов: <strong>{tariff.offer_analyses_count}</strong></span>
                </div>
              </div>
              
              <div className="mt-6 pt-4 border-t">
                <div className="flex items-baseline justify-between">
                  <span className="text-3xl font-bold text-primary-600">
                    {tariff.price.toLocaleString('ru-RU')} ₽
                  </span>
                </div>
              </div>
              
              <button
                type="button"
                className="w-full mt-4 bg-primary-600 text-white py-2 rounded-lg font-medium hover:bg-primary-700 transition-colors"
              >
                Выбрать тариф
              </button>
            </div>
          ))}
        </div>
      ) : (
        /* Форма оплаты выбранного тарифа */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6">
              {/* Информация о выбранном тарифе */}
              <div className="mb-6 pb-6 border-b">
                <button
                  onClick={() => {
                    setSelectedTariff(null)
                    setPaymentUrl('')
                    setError('')
                  }}
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium mb-4"
                >
                  ← Вернуться к выбору тарифа
                </button>
                <div className="flex items-center space-x-3 mb-2">
                  <Package className="w-6 h-6 text-primary-600" />
                  <h2 className="text-2xl font-bold text-gray-900">{selectedTariff.name}</h2>
                </div>
                <p className="text-gray-600 text-sm mb-4">{selectedTariff.description}</p>
                <div className="flex space-x-6 text-sm text-gray-700">
                  <span>📋 Вакансий: <strong>{selectedTariff.vacancies_count}</strong></span>
                  <span>🔍 Анализов: <strong>{selectedTariff.offer_analyses_count}</strong></span>
                </div>
                <div className="mt-4 text-2xl font-bold text-primary-600">
                  {selectedTariff.price.toLocaleString('ru-RU')} ₽
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4" />
                    <span>{error}</span>
                  </div>
                )}

                {paymentUrl && (
                  <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
                    <div className="flex items-center space-x-2 mb-3">
                      <CheckCircle className="w-5 h-5" />
                      <span className="font-medium">Платеж создан успешно!</span>
                    </div>
                    <a
                      href={paymentUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-block bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Перейти к оплате
                    </a>
                  </div>
                )}

                {/* Тип плательщика */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Тип плательщика *
                  </label>
                  <div className="flex space-x-4">
                    <label className={`flex items-center px-4 py-3 border-2 rounded-lg cursor-pointer transition-colors flex-1 ${
                      paymentType === 'individual' 
                        ? 'border-primary-500 bg-primary-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}>
                      <input
                        type="radio"
                        name="paymentType"
                        value="individual"
                        checked={paymentType === 'individual'}
                        onChange={(e) => setPaymentType(e.target.value)}
                        className="mr-2"
                      />
                      <User className="w-5 h-5 mr-2" />
                      <span>Физическое лицо</span>
                    </label>
                    <label className={`flex items-center px-4 py-3 border-2 rounded-lg cursor-pointer transition-colors flex-1 ${
                      paymentType === 'legal_entity' 
                        ? 'border-primary-500 bg-primary-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}>
                      <input
                        type="radio"
                        name="paymentType"
                        value="legal_entity"
                        checked={paymentType === 'legal_entity'}
                        onChange={(e) => setPaymentType(e.target.value)}
                        className="mr-2"
                      />
                      <Building2 className="w-5 h-5 mr-2" />
                      <span>Юридическое лицо</span>
                    </label>
                  </div>
                </div>

                {/* Поля для юридического лица */}
                {paymentType === 'legal_entity' && (
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
                        required
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
                        required
                        maxLength={12}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                        placeholder="1234567890"
                      />
                    </div>

                    <div>
                      <label htmlFor="kpp" className="block text-sm font-medium text-gray-700 mb-2">
                        КПП (опционально)
                      </label>
                      <input
                        id="kpp"
                        type="text"
                        value={kpp}
                        onChange={(e) => setKpp(e.target.value.replace(/\D/g, ''))}
                        maxLength={9}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                        placeholder="123456789"
                      />
                    </div>

                    <div>
                      <label htmlFor="legalAddress" className="block text-sm font-medium text-gray-700 mb-2">
                        Юридический адрес (опционально)
                      </label>
                      <input
                        id="legalAddress"
                        type="text"
                        value={legalAddress}
                        onChange={(e) => setLegalAddress(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                        placeholder="г. Москва, ул. Примерная, д. 1"
                      />
                    </div>

                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                        Email (опционально)
                      </label>
                      <input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                        placeholder="company@example.com"
                      />
                    </div>
                  </>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center justify-center space-x-2"
                >
                  <CreditCard className="w-5 h-5" />
                  <span>{loading ? 'Создание платежа...' : 'Создать платеж'}</span>
                </button>
              </form>
            </div>
          </div>

          {/* Информация */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <Sparkles className="w-5 h-5 text-primary-600" />
                <span>Информация</span>
              </h2>
              <div className="space-y-4 text-sm text-gray-600">
                <p>
                  <strong>Для физических лиц:</strong> Платеж будет обработан через платежную систему Selfwork.
                </p>
                <p>
                  <strong>Для юридических лиц:</strong> Будет создан счет на оплату. После оплаты вы получите документы.
                </p>
                {userInfo?.is_legal_entity && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <p className="text-blue-800 font-medium">Ваш профиль: Юридическое лицо</p>
                    {userInfo.company_name && (
                      <p className="text-blue-700 text-xs mt-1">Компания: {userInfo.company_name}</p>
                    )}
                    {userInfo.inn && (
                      <p className="text-blue-700 text-xs">ИНН: {userInfo.inn}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
