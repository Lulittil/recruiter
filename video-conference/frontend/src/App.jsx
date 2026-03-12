import { useState, useEffect } from 'react'
import LoginModal from './components/LoginModal'
import VideoRoom from './components/VideoRoom'
import axios from 'axios'

// Определяем API URL
const getApiUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  
  // Если работаем через nginx прокси, используем относительные пути
  // nginx проксирует /api к video-conference:8000
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // В dev режиме или при прямом подключении используем прямой порт
    const port = window.location.port
    if (port === '3001' || port === '80' || !port) {
      return 'http://localhost:8004'
    }
    return `${window.location.protocol}//${window.location.hostname}:8004`
  }
  
  // В продакшене через nginx используем текущий хост (nginx проксирует)
  return window.location.origin
}

const API_URL = getApiUrl()

function App() {
  // Получаем room_id из URL параметров
  const getRoomIdFromUrl = () => {
    const params = new URLSearchParams(window.location.search)
    return params.get('room')
  }

  const [roomId] = useState(getRoomIdFromUrl())
  const [participantInfo, setParticipantInfo] = useState(null)
  const [roomExists, setRoomExists] = useState(null)

  useEffect(() => {
    // Проверяем существование комнаты при загрузке
    if (roomId) {
      checkRoomExists(roomId)
    } else {
      setRoomExists(false)
    }
  }, [roomId])

  const checkRoomExists = async (roomId) => {
    try {
      const response = await axios.get(`${API_URL}/api/rooms/${roomId}`)
      if (response.data) {
        setRoomExists(true)
      }
    } catch (error) {
      console.error('Room check error:', error)
      // Не блокируем доступ - комната создастся автоматически при подключении
      // Просто показываем форму входа
      setRoomExists(true)
    }
  }

  const handleJoin = (name, email) => {
    setParticipantInfo({
      name,
      email,
      participant_id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    })
  }

  if (!roomId) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Ошибка</h1>
          <p className="text-gray-600 mb-6">Не указан ID комнаты в URL</p>
          <p className="text-sm text-gray-500">
            Используйте ссылку вида: <code className="bg-gray-100 px-2 py-1 rounded">/room?room=ROOM_ID</code>
          </p>
        </div>
      </div>
    )
  }

  // Убираем блокировку - комната создастся автоматически при подключении через WebSocket

  if (roomExists === null) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!participantInfo) {
    return <LoginModal onJoin={handleJoin} roomId={roomId} />
  }

  return (
    <VideoRoom
      roomId={roomId}
      participantInfo={participantInfo}
      apiUrl={API_URL}
    />
  )
}

export default App

