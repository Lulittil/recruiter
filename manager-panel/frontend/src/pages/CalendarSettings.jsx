import { useState, useEffect } from 'react'
import { calendarAPI } from '../api'

const DAYS_OF_WEEK = [
  { key: 'monday', label: 'Понедельник' },
  { key: 'tuesday', label: 'Вторник' },
  { key: 'wednesday', label: 'Среда' },
  { key: 'thursday', label: 'Четверг' },
  { key: 'friday', label: 'Пятница' },
  { key: 'saturday', label: 'Суббота' },
  { key: 'sunday', label: 'Воскресенье' },
]

export default function CalendarSettings() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [settings, setSettings] = useState({
    default_duration_minutes: 60,
    monday_start: '',
    monday_end: '',
    tuesday_start: '',
    tuesday_end: '',
    wednesday_start: '',
    wednesday_end: '',
    thursday_start: '',
    thursday_end: '',
    friday_start: '',
    friday_end: '',
    saturday_start: '',
    saturday_end: '',
    sunday_start: '',
    sunday_end: '',
  })

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const data = await calendarAPI.getSettings()
      setSettings({
        default_duration_minutes: data.default_duration_minutes || 60,
        monday_start: data.monday_start || '',
        monday_end: data.monday_end || '',
        tuesday_start: data.tuesday_start || '',
        tuesday_end: data.tuesday_end || '',
        wednesday_start: data.wednesday_start || '',
        wednesday_end: data.wednesday_end || '',
        thursday_start: data.thursday_start || '',
        thursday_end: data.thursday_end || '',
        friday_start: data.friday_start || '',
        friday_end: data.friday_end || '',
        saturday_start: data.saturday_start || '',
        saturday_end: data.saturday_end || '',
        sunday_start: data.sunday_start || '',
        sunday_end: data.sunday_end || '',
      })
    } catch (err) {
      console.error('Error loading settings:', err)
      setError('Ошибка загрузки настроек')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSaving(true)

    try {
      await calendarAPI.updateSettings(settings)
      alert('Настройки сохранены успешно!')
    } catch (err) {
      console.error('Error saving settings:', err)
      setError(err.response?.data?.detail || 'Ошибка сохранения настроек')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-gray-600">Загрузка настроек...</div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Настройки календаря</h1>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Дефолтная длительность */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Дефолтная длительность созвона</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Длительность (минуты)
            </label>
            <input
              type="number"
              min="15"
              step="15"
              value={settings.default_duration_minutes}
              onChange={(e) => handleChange('default_duration_minutes', parseInt(e.target.value) || 60)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
            <p className="mt-1 text-sm text-gray-500">
              Это время будет автоматически использоваться при создании событий "Собеседование", 
              а также для генерации доступных слотов для кандидатов (интервал между слотами).
            </p>
          </div>
        </div>

        {/* Рабочие часы */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Рабочие часы</h2>
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900 font-medium mb-2">
              💡 Для чего нужны эти настройки?
            </p>
            <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
              <li>Когда Вы отправляете кандидату команду "Пригласить" в Telegram, система автоматически создаст список доступных слотов на основе Ваших рабочих часов</li>
              <li>Кандидат увидит только те временные слоты, которые попадают в указанные рабочие часы</li>
              <li>Система автоматически исключит уже забронированное время</li>
              <li>Слоты будут генерироваться с интервалом, равным дефолтной длительности (см. выше)</li>
            </ul>
            <p className="text-sm text-blue-800 mt-2">
              <strong>Пример:</strong> Если Вы указали Понедельник 08:00-11:00 и дефолтная длительность 60 минут, 
              кандидат увидит слоты: 08:00, 09:00, 10:00 (если они не заняты).
            </p>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            Укажите время, когда Вы доступны для созвонов. Слоты будут автоматически генерироваться на основе этих часов.
          </p>

          <div className="space-y-4">
            {DAYS_OF_WEEK.map((day) => (
              <div key={day.key} className="flex items-center gap-4">
                <div className="w-32">
                  <label className="block text-sm font-medium text-gray-700">
                    {day.label}
                  </label>
                </div>
                <div className="flex-1 grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Начало</label>
                    <input
                      type="time"
                      value={settings[`${day.key}_start`]}
                      onChange={(e) => handleChange(`${day.key}_start`, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Конец</label>
                    <input
                      type="time"
                      value={settings[`${day.key}_end`]}
                      onChange={(e) => handleChange(`${day.key}_end`, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
                <div className="w-20">
                  <button
                    type="button"
                    onClick={() => {
                      handleChange(`${day.key}_start`, '')
                      handleChange(`${day.key}_end`, '')
                    }}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    Очистить
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Кнопка сохранения */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Сохранение...' : 'Сохранить настройки'}
          </button>
        </div>
      </form>
    </div>
  )
}

