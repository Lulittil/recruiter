import { useEffect, useState } from 'react'
import { Calendar as CalendarIcon, Plus, Edit, Trash2, ChevronLeft, ChevronRight, Grid, List } from 'lucide-react'
import { calendarAPI, candidatesAPI } from '../api'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, startOfWeek, endOfWeek, startOfDay, endOfDay, startOfWeek as startWeek, endOfWeek as endWeek, addDays, subDays, addWeeks, subWeeks, addMonths, subMonths, isSameWeek, isToday } from 'date-fns'
import ru from 'date-fns/locale/ru'

export default function Calendar() {
  const [viewMode, setViewMode] = useState('month') // 'day', 'week', 'month'
  const [currentDate, setCurrentDate] = useState(new Date())
  const [events, setEvents] = useState([])
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [showDayEventsModal, setShowDayEventsModal] = useState(false)
  const [selectedDay, setSelectedDay] = useState(null)
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [formData, setFormData] = useState({
    candidate_id: '',
    title: '',
    description: '',
    event_date: '',
    event_type: 'call',
    recurrence_type: 'none',
    recurrence_end_date: '',
    recurrence_interval: 1
  })


  const loadData = async () => {
    try {
      let start, end
      
      if (viewMode === 'day') {
        start = startOfDay(currentDate)
        end = endOfDay(currentDate)
      } else if (viewMode === 'week') {
        start = startOfDay(startWeek(currentDate, { locale: ru }))
        end = endOfDay(endWeek(currentDate, { locale: ru }))
      } else {
        start = startOfMonth(currentDate)
        end = endOfMonth(currentDate)
      }
      
      const [eventsData, candidatesData] = await Promise.all([
        calendarAPI.getEvents(start, end),
        candidatesAPI.getAll()
      ])
      
      setEvents(Array.isArray(eventsData) ? eventsData : [])
      setCandidates(Array.isArray(candidatesData) ? candidatesData : [])
    } catch (error) {
      console.error('Error loading calendar data:', error)
      setEvents([])
      setCandidates([])
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    loadData()
  }, [currentDate, viewMode])

  const handleOpenModal = (date = null, event = null) => {
    if (event) {
      setSelectedEvent(event)
      setFormData({
        candidate_id: event.candidate_id || '',
        title: event.title,
        description: event.description || '',
        event_date: format(new Date(event.event_date), "yyyy-MM-dd'T'HH:mm"),
        end_time: '',
        event_type: event.event_type,
        recurrence_type: event.recurrence_type || 'none',
        recurrence_end_date: event.recurrence_end_date ? format(new Date(event.recurrence_end_date), "yyyy-MM-dd'T'HH:mm") : '',
        recurrence_interval: event.recurrence_interval || 1
      })
    } else {
      setSelectedEvent(null)
      setFormData({
        candidate_id: '',
        title: '',
        description: '',
        event_date: date ? format(date, "yyyy-MM-dd'T'HH:mm") : '',
        end_time: '',
        event_type: 'call',
        recurrence_type: 'none',
        recurrence_end_date: '',
        recurrence_interval: 1
      })
    }
    setShowModal(true)
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setSelectedEvent(null)
      setFormData({
        candidate_id: '',
        title: '',
        description: '',
        event_date: '',
        end_time: '',
        event_type: 'call',
        recurrence_type: 'none',
        recurrence_end_date: '',
        recurrence_interval: 1
      })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const eventData = {
        ...formData,
        candidate_id: formData.candidate_id ? parseInt(formData.candidate_id) : null,
        event_date: new Date(formData.event_date).toISOString(),
        end_time: formData.end_time ? new Date(formData.end_time).toISOString() : null,
        recurrence_type: formData.recurrence_type === 'none' ? null : formData.recurrence_type,
        recurrence_end_date: formData.recurrence_end_date ? new Date(formData.recurrence_end_date).toISOString() : null,
        recurrence_interval: formData.recurrence_type !== 'none' ? parseInt(formData.recurrence_interval) : null
      }

      if (selectedEvent) {
        await calendarAPI.updateEvent(selectedEvent.event_id, eventData)
      } else {
        // API теперь возвращает массив событий (для повторяющихся)
        await calendarAPI.createEvent(eventData)
      }
      
      handleCloseModal()
      loadData()
    } catch (error) {
      console.error('Error saving event:', error)
      alert('Ошибка при сохранении события')
    }
  }

  const handleDelete = async (eventId) => {
    if (!confirm('Удалить событие?')) return
    
    try {
      await calendarAPI.deleteEvent(eventId)
      loadData()
    } catch (error) {
      console.error('Error deleting event:', error)
      alert('Ошибка при удалении события')
    }
  }

  const getEventsForDate = (date) => {
    return events.filter(event => isSameDay(new Date(event.event_date), date))
  }
  
  const handleDayClick = (day) => {
    const dayEvents = getEventsForDate(day)
    setSelectedDay(day)
    setShowDayEventsModal(true)
  }
  
  const navigateDate = (direction) => {
    if (viewMode === 'day') {
      setCurrentDate(direction === 'next' ? addDays(currentDate, 1) : subDays(currentDate, 1))
    } else if (viewMode === 'week') {
      setCurrentDate(direction === 'next' ? addWeeks(currentDate, 1) : subWeeks(currentDate, 1))
    } else {
      setCurrentDate(direction === 'next' ? addMonths(currentDate, 1) : subMonths(currentDate, 1))
    }
  }
  
  const getViewTitle = () => {
    if (viewMode === 'day') {
      return format(currentDate, 'd MMMM yyyy', { locale: ru })
    } else if (viewMode === 'week') {
      const weekStart = startWeek(currentDate, { locale: ru })
      const weekEnd = endWeek(currentDate, { locale: ru })
      return `${format(weekStart, 'd MMM', { locale: ru })} - ${format(weekEnd, 'd MMM yyyy', { locale: ru })}`
    } else {
      return format(currentDate, 'LLLL yyyy', { locale: ru })
    }
  }

  const monthStart = startOfMonth(currentDate)
  const monthEnd = endOfMonth(currentDate)
  const calendarStart = startOfWeek(monthStart, { locale: ru })
  const calendarEnd = endOfWeek(monthEnd, { locale: ru })
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const renderDayView = () => {
    const dayEvents = getEventsForDate(currentDate)
    const hours = Array.from({ length: 24 }, (_, i) => i)
    
    return (
      <div className="space-y-2">
        {hours.map(hour => {
          const hourEvents = dayEvents.filter(event => {
            const eventHour = new Date(event.event_date).getHours()
            return eventHour === hour
          })
          
          return (
            <div key={hour} className="flex border-b border-gray-200">
              <div className="w-20 text-sm text-gray-500 py-2 px-2">
                {String(hour).padStart(2, '0')}:00
              </div>
              <div className="flex-1 py-2">
                {hourEvents.map(event => (
                  <div
                    key={event.event_id}
                    className="mb-1 p-2 bg-primary-100 text-primary-700 rounded cursor-pointer hover:bg-primary-200"
                    onClick={() => handleOpenModal(null, event)}
                  >
                    <div className="font-medium">{event.title}</div>
                    <div className="text-xs text-gray-600">
                      {format(new Date(event.event_date), 'HH:mm')} - {event.duration_minutes ? `${format(new Date(new Date(event.event_date).getTime() + event.duration_minutes * 60000), 'HH:mm')}` : ''}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>
    )
  }
  
  const renderWeekView = () => {
    const weekStart = startWeek(currentDate, { locale: ru })
    const weekDays = eachDayOfInterval({ start: weekStart, end: endWeek(currentDate, { locale: ru }) })
    
    return (
      <div className="grid grid-cols-7 gap-2">
        {weekDays.map((day) => {
          const dayEvents = getEventsForDate(day)
          const isCurrentMonth = isSameMonth(day, currentDate)
          const isCurrentDay = isToday(day)
          
          return (
            <div
              key={day.toISOString()}
              className={`min-h-32 p-2 border rounded-lg ${
                isCurrentMonth ? 'bg-white' : 'bg-gray-50'
              } ${isCurrentDay ? 'ring-2 ring-primary-500' : ''}`}
            >
              <div className={`text-sm font-medium mb-2 ${isCurrentMonth ? 'text-gray-900' : 'text-gray-400'}`}>
                {format(day, 'd EEE', { locale: ru })}
              </div>
              <div className="space-y-1">
                {dayEvents.slice(0, 3).map((event) => (
                  <div
                    key={event.event_id}
                    className="text-xs p-1 bg-primary-100 text-primary-700 rounded truncate cursor-pointer hover:bg-primary-200"
                    onClick={() => handleOpenModal(null, event)}
                    title={event.title}
                  >
                    {format(new Date(event.event_date), 'HH:mm')} {event.title}
                  </div>
                ))}
                {dayEvents.length > 3 && (
                  <button
                    onClick={() => handleDayClick(day)}
                    className="text-xs text-primary-600 hover:text-primary-800"
                  >
                    +{dayEvents.length - 3} еще
                  </button>
                )}
              </div>
              <button
                onClick={() => handleOpenModal(day)}
                className="mt-1 w-full text-xs text-gray-400 hover:text-primary-600"
              >
                +
              </button>
            </div>
          )
        })}
      </div>
    )
  }
  
  const renderMonthView = () => {
    const monthStart = startOfMonth(currentDate)
    const monthEnd = endOfMonth(currentDate)
    const calendarStart = startOfWeek(monthStart, { locale: ru })
    const calendarEnd = endOfWeek(monthEnd, { locale: ru })
    const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd })
    
    return (
      <div className="grid grid-cols-7 gap-2">
        {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map((day) => (
          <div key={day} className="text-center font-semibold text-gray-700 py-2">
            {day}
          </div>
        ))}
        
        {days.map((day) => {
          const dayEvents = getEventsForDate(day)
          const isCurrentMonth = isSameMonth(day, currentDate)
          const isCurrentDay = isToday(day)
          
          return (
            <div
              key={day.toISOString()}
              className={`min-h-24 p-2 border rounded-lg ${
                isCurrentMonth ? 'bg-white' : 'bg-gray-50'
              } ${isCurrentDay ? 'ring-2 ring-primary-500' : ''}`}
            >
              <div className={`text-sm font-medium mb-1 ${isCurrentMonth ? 'text-gray-900' : 'text-gray-400'}`}>
                {format(day, 'd')}
              </div>
              <div className="space-y-1">
                {dayEvents.slice(0, 2).map((event) => (
                  <div
                    key={event.event_id}
                    className="text-xs p-1 bg-primary-100 text-primary-700 rounded truncate cursor-pointer hover:bg-primary-200"
                    onClick={() => handleOpenModal(null, event)}
                    title={event.title}
                  >
                    {format(new Date(event.event_date), 'HH:mm')} {event.title}
                  </div>
                ))}
                {dayEvents.length > 2 && (
                  <button
                    onClick={() => handleDayClick(day)}
                    className="text-xs text-primary-600 hover:text-primary-800"
                  >
                    +{dayEvents.length - 2} еще
                  </button>
                )}
              </div>
              <button
                onClick={() => handleOpenModal(day)}
                className="mt-1 w-full text-xs text-gray-400 hover:text-primary-600"
              >
                +
              </button>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Календарь</h1>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('day')}
              className={`px-3 py-1 rounded ${viewMode === 'day' ? 'bg-white shadow' : ''}`}
              title="День"
            >
              <List className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('week')}
              className={`px-3 py-1 rounded ${viewMode === 'week' ? 'bg-white shadow' : ''}`}
              title="Неделя"
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('month')}
              className={`px-3 py-1 rounded ${viewMode === 'month' ? 'bg-white shadow' : ''}`}
              title="Месяц"
            >
              <CalendarIcon className="w-4 h-4" />
            </button>
          </div>
          <button
            onClick={() => handleOpenModal()}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Добавить событие</span>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigateDate('prev')}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg flex items-center"
          >
            <ChevronLeft className="w-5 h-5" />
            <span className="ml-1">Предыдущий</span>
          </button>
          <h2 className="text-xl font-semibold">
            {getViewTitle()}
          </h2>
          <button
            onClick={() => navigateDate('next')}
            className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg flex items-center"
          >
            <span className="mr-1">Следующий</span>
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {viewMode === 'day' && renderDayView()}
        {viewMode === 'week' && renderWeekView()}
        {viewMode === 'month' && renderMonthView()}

      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4">
              {selectedEvent ? 'Редактировать событие' : 'Новое событие'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Кандидат (опционально)
                </label>
                <select
                  value={formData.candidate_id}
                  onChange={(e) => setFormData({ ...formData, candidate_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Не указан (слот свободного времени)</option>
                  {candidates.map((candidate) => (
                    <option key={candidate.applicant_id} value={candidate.applicant_id}>
                      {candidate.full_name || `Кандидат #${candidate.applicant_id}`}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Название
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Дата и время начала
                </label>
                <input
                  type="datetime-local"
                  value={formData.event_date}
                  onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>

              {formData.event_type === 'slot' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Время окончания (для создания диапазона слотов)
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Если указано, будет создано несколько слотов в указанном диапазоне. Может пересекаться с другими мероприятиями.
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Тип
                </label>
                <select
                  value={formData.event_type}
                  onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="call">Созвон</option>
                  <option value="meeting">Встреча</option>
                  <option value="interview">Собеседование</option>
                  <option value="slot">Слот свободного времени</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Описание
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Повторение
                </label>
                <select
                  value={formData.recurrence_type}
                  onChange={(e) => setFormData({ ...formData, recurrence_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="none">Не повторять</option>
                  <option value="daily">Ежедневно</option>
                  <option value="weekly">Еженедельно</option>
                  <option value="monthly">Ежемесячно</option>
                </select>
              </div>

              {formData.recurrence_type !== 'none' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Повторять каждые
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={formData.recurrence_interval}
                      onChange={(e) => setFormData({ ...formData, recurrence_interval: parseInt(e.target.value) || 1 })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                    <span className="text-xs text-gray-500 mt-1 block">
                      {formData.recurrence_type === 'daily' && 'дней'}
                      {formData.recurrence_type === 'weekly' && 'недель'}
                      {formData.recurrence_type === 'monthly' && 'месяцев'}
                    </span>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Повторять до
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.recurrence_end_date}
                      onChange={(e) => setFormData({ ...formData, recurrence_end_date: e.target.value })}
                      required={formData.recurrence_type !== 'none'}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </>
              )}

              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700"
                >
                  {selectedEvent ? 'Сохранить' : 'Создать'}
                </button>
                {selectedEvent && (
                  <button
                    type="button"
                    onClick={() => handleDelete(selectedEvent.event_id)}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Удалить</span>
                  </button>
                )}
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300"
                >
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDayEventsModal && selectedDay && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              События на {format(selectedDay, 'd MMMM yyyy', { locale: ru })}
            </h2>
            
            <div className="space-y-2 mb-4">
              {getEventsForDate(selectedDay).length === 0 ? (
                <p className="text-gray-500">Нет событий на этот день</p>
              ) : (
                getEventsForDate(selectedDay)
                  .sort((a, b) => new Date(a.event_date) - new Date(b.event_date))
                  .map((event) => (
                    <div
                      key={event.event_id}
                      className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setShowDayEventsModal(false)
                        handleOpenModal(null, event)
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{event.title}</div>
                          <div className="text-sm text-gray-600 mt-1">
                            {format(new Date(event.event_date), 'HH:mm', { locale: ru })} - {event.duration_minutes ? format(new Date(new Date(event.event_date).getTime() + event.duration_minutes * 60000), 'HH:mm', { locale: ru }) : ''}
                          </div>
                          {event.description && (
                            <div className="text-sm text-gray-500 mt-1">{event.description}</div>
                          )}
                          {event.candidate_id && (
                            <div className="text-xs text-primary-600 mt-1">
                              Кандидат: {candidates.find(c => c.applicant_id === event.candidate_id)?.full_name || `#${event.candidate_id}`}
                            </div>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleOpenModal(null, event)
                              setShowDayEventsModal(false)
                            }}
                            className="p-2 text-primary-600 hover:bg-primary-50 rounded"
                            title="Редактировать"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDelete(event.event_id)
                              setShowDayEventsModal(false)
                            }}
                            className="p-2 text-red-600 hover:bg-red-50 rounded"
                            title="Удалить"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
              )}
            </div>
            
            <div className="flex justify-end">
              <button
                onClick={() => {
                  setShowDayEventsModal(false)
                  setSelectedDay(null)
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

