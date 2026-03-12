import { useState, useEffect, useRef } from 'react'
import { Video, VideoOff, Mic, MicOff, MessageCircle, Users, LogOut, Download } from 'lucide-react'
import SimplePeer from 'simple-peer'

export default function VideoRoom({ roomId, participantInfo, apiUrl }) {
  const [localStream, setLocalStream] = useState(null)
  const [remoteStreams, setRemoteStreams] = useState({}) // participant_id -> stream
  const [participants, setParticipants] = useState([])
  const [totalParticipants, setTotalParticipants] = useState(1) // Начинаем с 1 (текущий пользователь)
  const [isVideoEnabled, setIsVideoEnabled] = useState(true)
  const [isAudioEnabled, setIsAudioEnabled] = useState(true)
  const [messages, setMessages] = useState([])
  const [messageText, setMessageText] = useState('')
  const [showChat, setShowChat] = useState(false)
  const [peers, setPeers] = useState({}) // participant_id -> peer instance
  const [isConnected, setIsConnected] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [isManager, setIsManager] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const localVideoRef = useRef(null)
  const localVideoForegroundRef = useRef(null) // Для переднего слоя с четким изображением
  const remoteVideoRefs = useRef({})
  const remoteVideoBackgroundRefs = useRef({}) // Для фоновых слоев удаленных видео
  const wsRef = useRef(null)
  const participantsRef = useRef([])
  const recognitionRef = useRef(null)

  // Загружаем сохраненные сообщения из localStorage при монтировании
  useEffect(() => {
    const savedMessages = localStorage.getItem(`chat_${roomId}`)
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages)
        setMessages(parsed)
      } catch (e) {
        console.error('Error loading saved messages:', e)
      }
    }
    
    // Проверяем статус менеджера сразу, если email уже есть
    if (participantInfo?.email) {
      console.log('Checking manager status on mount, email:', participantInfo.email)
      checkManagerStatus(participantInfo.email)
    }
  }, [roomId])

  // Сохраняем сообщения в localStorage при изменении
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chat_${roomId}`, JSON.stringify(messages))
    }
  }, [messages, roomId])

  useEffect(() => {
    initializeWebRTC()
    return () => {
      cleanup()
    }
  }, [])

  useEffect(() => {
    if (localStream) {
      // Применяем поток к обоим видео элементам (фон и передний план)
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = localStream
      }
      if (localVideoForegroundRef.current) {
        localVideoForegroundRef.current.srcObject = localStream
      }
    }
  }, [localStream])

  useEffect(() => {
    // Обновляем видео элементы для удаленных потоков
    Object.keys(remoteStreams).forEach(participantId => {
      const stream = remoteStreams[participantId]
      
      // Фоновый слой с размытием
      const bgVideoElement = remoteVideoBackgroundRefs.current[participantId]
      if (bgVideoElement && stream) {
        bgVideoElement.srcObject = stream
      }
      
      // Передний слой с четким изображением
      const fgVideoElement = remoteVideoRefs.current[participantId]
      if (fgVideoElement && stream) {
        fgVideoElement.srcObject = stream
      }
    })
  }, [remoteStreams])

  const initializeWebRTC = async () => {
    try {
      // Получаем доступ к камере и микрофону
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      })
      setLocalStream(stream)

      // Подключаемся к WebSocket
      // Определяем правильный WebSocket URL
      let wsUrl
      if (apiUrl.startsWith('http://')) {
        wsUrl = apiUrl.replace('http://', 'ws://') + `/ws/${roomId}`
      } else if (apiUrl.startsWith('https://')) {
        wsUrl = apiUrl.replace('https://', 'wss://') + `/ws/${roomId}`
      } else {
        // Если apiUrl не содержит протокол, используем текущий протокол
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host.replace(':3001', ':8004').replace(':80', ':8004')
        wsUrl = `${protocol}//${host}/ws/${roomId}`
      }
      
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        // Отправляем сообщение о присоединении
        ws.send(JSON.stringify({
          type: 'join',
          participant_id: participantInfo.participant_id,
          name: participantInfo.name,
          email: participantInfo.email
        }))
        setIsConnected(true)
      }

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)

        if (message.type === 'joined') {
          const allParticipants = message.participants || []
          // Фильтруем, чтобы не включать текущего пользователя в список других участников
          const otherParticipants = allParticipants.filter(id => id !== participantInfo.participant_id)
          setParticipants(otherParticipants)
          participantsRef.current = otherParticipants
          // Обновляем общее количество участников
          setTotalParticipants(allParticipants.length)
          
          // Проверяем, является ли пользователь менеджером
          if (participantInfo.email) {
            console.log('Checking manager status after join, email:', participantInfo.email)
            checkManagerStatus(participantInfo.email)
          } else {
            console.warn('No email in participantInfo:', participantInfo)
          }
          
          // Загружаем историю сообщений из транскрипции
          if (message.transcript && Array.isArray(message.transcript)) {
            const chatMessages = message.transcript
              .filter(entry => entry.type === 'message' || entry.type === 'transcript')
              .map(entry => ({
                from: entry.participant_id,
                name: entry.name || entry.participant_id,
                text: entry.text,
                timestamp: entry.timestamp
              }))
            // Объединяем с уже сохраненными сообщениями, избегая дубликатов
            setMessages(prev => {
              const existingIds = new Set(prev.map(m => `${m.from}_${m.timestamp}`))
              const newMessages = chatMessages.filter(m => 
                !existingIds.has(`${m.from}_${m.timestamp}`)
              )
              return [...prev, ...newMessages].sort((a, b) => 
                new Date(a.timestamp) - new Date(b.timestamp)
              )
            })
          }
          
          // Создаем P2P соединения с существующими участниками
          otherParticipants.forEach(participantId => {
            createPeer(participantId, false, ws)
          })
        } else if (message.type === 'participant_joined') {
          if (message.participant_id !== participantInfo.participant_id) {
            const allParticipants = message.participants || []
            const otherParticipants = allParticipants.filter(id => id !== participantInfo.participant_id)
            setParticipants(otherParticipants)
            participantsRef.current = otherParticipants
            setTotalParticipants(allParticipants.length)
            // Создаем новое P2P соединение
            createPeer(message.participant_id, true, ws)
          } else {
            // Если это мы сами присоединились, обновляем счетчик
            setTotalParticipants((message.participants || []).length)
          }
        } else if (message.type === 'participant_left') {
          const allParticipants = message.participants || []
          const otherParticipants = allParticipants.filter(id => id !== participantInfo.participant_id)
          setParticipants(otherParticipants)
          participantsRef.current = otherParticipants
          setTotalParticipants(allParticipants.length)
          // Закрываем P2P соединение
          if (peers[message.participant_id]) {
            peers[message.participant_id].destroy()
            setPeers(prev => {
              const newPeers = { ...prev }
              delete newPeers[message.participant_id]
              return newPeers
            })
            setRemoteStreams(prev => {
              const newStreams = { ...prev }
              delete newStreams[message.participant_id]
              return newStreams
            })
          }
        } else if (message.type === 'offer') {
          handleOffer(message, ws)
        } else if (message.type === 'answer') {
          handleAnswer(message)
        } else if (message.type === 'ice_candidate') {
          handleIceCandidate(message)
        } else if (message.type === 'message') {
          setMessages(prev => [...prev, {
            from: message.from,
            name: message.name,
            text: message.text,
            timestamp: message.timestamp
          }])
        } else if (message.type === 'transcript') {
          // Транскрипция речи от другого участника
          setMessages(prev => [...prev, {
            from: message.from,
            name: message.name || message.from,
            text: message.text,
            timestamp: message.timestamp
          }])
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        setIsConnected(false)
        cleanup()
      }

      wsRef.current = ws

      // Инициализируем распознавание речи
      initializeSpeechRecognition()

    } catch (error) {
      console.error('Error initializing WebRTC:', error)
      alert('Не удалось получить доступ к камере/микрофону. Проверьте разрешения.')
    }
  }

  const initializeSpeechRecognition = () => {
    // Проверяем поддержку Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported in this browser')
      return
    }

    try {
      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'ru-RU' // Русский язык

      recognition.onstart = () => {
        setIsTranscribing(true)
        console.log('Speech recognition started')
      }

      recognition.onresult = (event) => {
        let finalTranscript = ''
        let interimTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' '
          } else {
            interimTranscript += transcript
          }
        }

        // Отправляем только финальный результат
        if (finalTranscript.trim() && wsRef.current) {
          const message = {
            type: 'transcript',
            text: finalTranscript.trim(),
            timestamp: new Date().toISOString()
          }
          wsRef.current.send(JSON.stringify(message))
        }
      }

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        if (event.error === 'no-speech' || event.error === 'audio-capture') {
          // Не критичные ошибки, продолжаем работу
          return
        }
        // Для других ошибок можно остановить распознавание
        if (event.error === 'not-allowed') {
          console.warn('Speech recognition not allowed')
          setIsTranscribing(false)
        }
      }

      recognition.onend = () => {
        setIsTranscribing(false)
        // Автоматически перезапускаем, если аудио включено
        if (isAudioEnabled && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          try {
            recognition.start()
          } catch (e) {
            // Возможно уже запущено, игнорируем ошибку
            console.log('Recognition restart skipped:', e.message)
          }
        }
      }

      recognitionRef.current = recognition

      // Запускаем распознавание, если аудио включено
      if (isAudioEnabled) {
        recognition.start()
      }
    } catch (error) {
      console.error('Error initializing speech recognition:', error)
    }
  }

  const createPeer = (participantId, isInitiator, ws) => {
    const peer = new SimplePeer({
      initiator: isInitiator,
      trickle: false,
      stream: localStream
    })

    peer.on('signal', (data) => {
      if (data.type === 'offer') {
        ws.send(JSON.stringify({
          type: 'offer',
          to: participantId,
          offer: data
        }))
      } else if (data.type === 'answer') {
        ws.send(JSON.stringify({
          type: 'answer',
          to: participantId,
          answer: data
        }))
      } else if (data.candidate) {
        ws.send(JSON.stringify({
          type: 'ice_candidate',
          to: participantId,
          candidate: data
        }))
      }
    })

    peer.on('stream', (stream) => {
      setRemoteStreams(prev => ({
        ...prev,
        [participantId]: stream
      }))
    })

    peer.on('close', () => {
      setRemoteStreams(prev => {
        const newStreams = { ...prev }
        delete newStreams[participantId]
        return newStreams
      })
    })

    setPeers(prev => ({
      ...prev,
      [participantId]: peer
    }))
  }

  const handleOffer = (message, ws) => {
    const peer = new SimplePeer({
      initiator: false,
      trickle: false,
      stream: localStream
    })

    peer.on('signal', (data) => {
      if (data.type === 'answer') {
        ws.send(JSON.stringify({
          type: 'answer',
          to: message.from,
          answer: data
        }))
      } else if (data.candidate) {
        ws.send(JSON.stringify({
          type: 'ice_candidate',
          to: message.from,
          candidate: data
        }))
      }
    })

    peer.on('stream', (stream) => {
      setRemoteStreams(prev => ({
        ...prev,
        [message.from]: stream
      }))
    })

    peer.signal(message.offer)

    setPeers(prev => ({
      ...prev,
      [message.from]: peer
    }))
  }

  const handleAnswer = (message) => {
    const peer = peers[message.from]
    if (peer) {
      peer.signal(message.answer)
    }
  }

  const handleIceCandidate = (message) => {
    const peer = peers[message.from]
    if (peer) {
      peer.signal(message.candidate)
    }
  }

  const toggleVideo = () => {
    if (localStream) {
      const videoTrack = localStream.getVideoTracks()[0]
      if (videoTrack) {
        videoTrack.enabled = !isVideoEnabled
        setIsVideoEnabled(!isVideoEnabled)
      }
    }
  }

  const toggleAudio = () => {
    if (localStream) {
      const audioTrack = localStream.getAudioTracks()[0]
      if (audioTrack) {
        const newState = !isAudioEnabled
        audioTrack.enabled = newState
        setIsAudioEnabled(newState)
        
        // Управляем распознаванием речи
        if (recognitionRef.current) {
          if (newState) {
            try {
              recognitionRef.current.start()
            } catch (e) {
              console.log('Recognition start skipped:', e.message)
            }
          } else {
            recognitionRef.current.stop()
          }
        }
      }
    }
  }

  const sendMessage = () => {
    if (!messageText.trim() || !wsRef.current) return

    const text = messageText.trim()
    const timestamp = new Date().toISOString()

    // Сразу добавляем сообщение локально, чтобы пользователь видел его сразу
    setMessages(prev => [...prev, {
      from: participantInfo.participant_id,
      name: participantInfo.name,
      text: text,
      timestamp: timestamp
    }])

    const message = {
      type: 'message',
      text: text,
      timestamp: timestamp
    }

    wsRef.current.send(JSON.stringify(message))
    setMessageText('')
  }

  const checkManagerStatus = async (email) => {
    if (!email) {
      console.warn('checkManagerStatus called without email')
      setIsManager(false)
      return
    }
    
    try {
      const apiUrl = getApiUrl()
      console.log('Checking manager status for email:', email, 'API URL:', apiUrl)
      const response = await fetch(`${apiUrl}/api/managers/check-by-email/${encodeURIComponent(email)}`)
      
      if (!response.ok) {
        console.error('Manager check failed:', response.status, response.statusText)
        setIsManager(false)
        return
      }
      
      const data = await response.json()
      console.log('Manager status response:', data)
      const isManagerStatus = data.is_manager || false
      setIsManager(isManagerStatus)
      console.log('Manager status set to:', isManagerStatus)
    } catch (error) {
      console.error('Error checking manager status:', error)
      setIsManager(false)
    }
  }

  const handleAnalyzeDialogue = async () => {
    if (!participantInfo.email) {
      alert('Email не найден. Нельзя проанализировать диалог.')
      return
    }

    setIsAnalyzing(true)
    try {
      const apiUrl = getApiUrl()
      const response = await fetch(`${apiUrl}/api/rooms/${roomId}/analyze-dialogue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: participantInfo.email
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Ошибка при анализе диалога')
      }

      const data = await response.json()
      alert('Анализ диалога завершен и отправлен менеджеру в Telegram!')
    } catch (error) {
      console.error('Error analyzing dialogue:', error)
      alert(`Ошибка при анализе диалога: ${error.message}`)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleLeave = () => {
    // Очищаем сохраненные сообщения при выходе
    localStorage.removeItem(`chat_${roomId}`)
    cleanup()
    window.location.href = '/'
  }

  const getApiUrl = () => {
    const hostname = window.location.hostname
    const protocol = window.location.protocol
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return `${protocol}//${hostname}:8004`
    }
    return `${protocol}//${hostname}`
  }

  const handleSaveTranscript = async () => {
    try {
      // Используем относительный путь, так как nginx проксирует /api
      const apiBase = apiUrl.includes('localhost:8004') || apiUrl.includes('127.0.0.1:8004') 
        ? apiUrl 
        : window.location.origin
      
      const response = await fetch(`${apiBase}/api/rooms/${roomId}/save-transcript`, {
        method: 'POST'
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Ошибка сервера' }))
        throw new Error(errorData.detail || 'Ошибка при сохранении транскрипции')
      }
      
      const data = await response.json()
      
      // Автоматически скачиваем файл
      if (data.download_url) {
        // Формируем полный URL для скачивания
        const downloadUrl = data.download_url.startsWith('http') 
          ? data.download_url 
          : `${apiBase}${data.download_url}`
        
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = data.filename || `transcript_${roomId}.txt`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        // Показываем уведомление об успехе
        alert(`Транскрипция сохранена и загружена: ${data.filename}`)
      } else {
        alert(`Транскрипция сохранена: ${data.filepath || data.message}`)
      }
    } catch (error) {
      console.error('Error saving transcript:', error)
      alert(error.message || 'Ошибка при сохранении транскрипции')
    }
  }

  const cleanup = () => {
    // Останавливаем распознавание речи
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (e) {
        // Игнорируем ошибки при остановке
      }
      recognitionRef.current = null
    }

    // Останавливаем локальный поток
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop())
    }

    // Закрываем все P2P соединения
    Object.values(peers).forEach(peer => {
      if (peer.destroy) peer.destroy()
    })

    // Закрываем WebSocket
    if (wsRef.current) {
      wsRef.current.close()
    }
  }

  const remoteParticipants = Object.keys(remoteStreams)

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold">Видеоконференция</h1>
          <div className="flex items-center space-x-2 text-sm text-gray-400">
            <Users className="w-4 h-4" />
            <span>{totalParticipants} участников</span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {isManager && (
            <>
              <button
                onClick={handleAnalyzeDialogue}
                disabled={isAnalyzing}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg flex items-center space-x-2 transition-colors"
              >
                {isAnalyzing ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    <span>Анализ...</span>
                  </>
                ) : (
                  <>
                    <span>📊</span>
                    <span>Анализировать диалог</span>
                  </>
                )}
              </button>
              <button
                onClick={handleSaveTranscript}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg flex items-center space-x-2 transition-colors"
              >
                <Download className="w-4 h-4" />
                <span>Скачать транскрипцию</span>
              </button>
            </>
          )}
          <button
            onClick={handleLeave}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Выйти</span>
          </button>
        </div>
      </div>

      <div className="flex h-[calc(100vh-73px)]">
        {/* Видео контейнер */}
        <div className="flex-1 p-4 grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto">
          {/* Локальное видео с размытым фоном */}
          <div className="relative bg-gray-800 rounded-lg overflow-hidden" style={{ position: 'relative' }}>
            {/* Фоновый слой с размытием */}
            <video
              ref={localVideoRef}
              autoPlay
              muted
              playsInline
              className="w-full h-full object-cover"
              style={{
                filter: 'blur(20px)',
                transform: 'scale(1.2)',
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: 0
              }}
            />
            {/* Передний слой с четким изображением (область лица и верхней части тела) */}
            <video
              ref={localVideoForegroundRef}
              autoPlay
              muted
              playsInline
              className="w-full h-full object-cover"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: 1,
                clipPath: 'ellipse(40% 55% at 50% 48%)',
                WebkitClipPath: 'ellipse(40% 55% at 50% 48%)'
              }}
            />
            <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 px-3 py-1 rounded z-10">
              {participantInfo.name} (Вы)
            </div>
            {!isVideoEnabled && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-20">
                <VideoOff className="w-16 h-16 text-gray-600" />
              </div>
            )}
          </div>

          {/* Удаленные видео с размытым фоном */}
          {remoteParticipants.map(participantId => (
            <div key={participantId} className="relative bg-gray-800 rounded-lg overflow-hidden" style={{ position: 'relative' }}>
              {/* Фоновый слой с размытием */}
              <video
                ref={el => {
                  if (el) {
                    remoteVideoBackgroundRefs.current[participantId] = el
                    const stream = remoteStreams[participantId]
                    if (stream) {
                      el.srcObject = stream
                    }
                  }
                }}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
                style={{
                  filter: 'blur(20px)',
                  transform: 'scale(1.2)',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  zIndex: 0
                }}
              />
              {/* Передний слой с четким изображением (область лица и верхней части тела) */}
              <video
                ref={el => {
                  if (el) {
                    remoteVideoRefs.current[participantId] = el
                    const stream = remoteStreams[participantId]
                    if (stream) {
                      el.srcObject = stream
                    }
                  }
                }}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  zIndex: 1,
                  clipPath: 'ellipse(40% 55% at 50% 48%)',
                  WebkitClipPath: 'ellipse(40% 55% at 50% 48%)'
                }}
              />
              <div className="absolute bottom-4 left-4 bg-black bg-opacity-50 px-3 py-1 rounded z-10">
                {participantId}
              </div>
            </div>
          ))}

          {remoteParticipants.length === 0 && (
            <div className="col-span-2 flex items-center justify-center">
              <div className="text-center">
                <Users className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                <p className="text-gray-400">Ожидание других участников...</p>
              </div>
            </div>
          )}
        </div>

        {/* Чат (боковая панель) */}
        {showChat && (
          <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col">
            <div className="p-4 border-b border-gray-700">
              <h2 className="font-semibold">Чат</h2>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {messages.map((msg, idx) => (
                <div key={idx} className="mb-3">
                  <div className="text-xs text-gray-400 mb-1">
                    {msg.name || msg.from} - {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="bg-gray-700 rounded-lg px-3 py-2">
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>
            <div className="p-4 border-t border-gray-700">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Введите сообщение..."
                  className="flex-1 bg-gray-700 text-white px-3 py-2 rounded-lg outline-none focus:ring-2 focus:ring-primary-500"
                />
                <button
                  onClick={sendMessage}
                  className="bg-primary-600 hover:bg-primary-700 px-4 py-2 rounded-lg transition-colors"
                >
                  Отправить
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Панель управления */}
      <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-gray-800 rounded-full px-6 py-3 flex items-center space-x-4 shadow-lg">
        <button
          onClick={toggleVideo}
          className={`p-3 rounded-full transition-colors ${
            isVideoEnabled ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-600 hover:bg-red-700'
          }`}
        >
          {isVideoEnabled ? <Video className="w-6 h-6" /> : <VideoOff className="w-6 h-6" />}
        </button>
        <button
          onClick={toggleAudio}
          className={`p-3 rounded-full transition-colors relative ${
            isAudioEnabled ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-600 hover:bg-red-700'
          }`}
          title={isAudioEnabled ? 'Микрофон включен' : 'Микрофон выключен'}
        >
          {isAudioEnabled ? <Mic className="w-6 h-6" /> : <MicOff className="w-6 h-6" />}
          {isTranscribing && (
            <span className="absolute top-0 right-0 w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          )}
        </button>
        <button
          onClick={() => setShowChat(!showChat)}
          className={`p-3 rounded-full transition-colors ${
            showChat ? 'bg-primary-600 hover:bg-primary-700' : 'bg-gray-700 hover:bg-gray-600'
          }`}
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      </div>
    </div>
  )
}

