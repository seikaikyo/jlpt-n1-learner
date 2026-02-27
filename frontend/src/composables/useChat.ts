import { ref, computed } from 'vue'

export type JlptLevel = 'n5' | 'n4' | 'n3' | 'n2' | 'n1'

export interface TTSSegment {
  text: string
  speaker: string | null
  lang: 'ja' | 'zh'
  pause_after: 'none' | 'short' | 'long'
  pause_before?: 'speaker'
  voice?: 'female' | 'male'
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  parsed?: Record<string, unknown>
  ttsSegments?: TTSSegment[]
  timestamp: Date
}

const API_BASE = 'http://localhost:8002'

export function useChat() {
  const messages = ref<Message[]>([])
  const currentMode = ref<'grammar' | 'reading' | 'conversation'>('grammar')
  const currentLevel = ref<JlptLevel>((localStorage.getItem('jlptLevel') as JlptLevel) || 'n3')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // API key 管理
  const apiEnabled = ref(localStorage.getItem('apiEnabled') === 'true')
  const apiKey = ref(localStorage.getItem('apiKey') || '')

  function setApiEnabled(value: boolean) {
    apiEnabled.value = value
    localStorage.setItem('apiEnabled', String(value))
  }

  function setApiKey(key: string) {
    apiKey.value = key
    localStorage.setItem('apiKey', key)
  }

  function setLevel(level: JlptLevel) {
    currentLevel.value = level
    localStorage.setItem('jlptLevel', level)
    clearMessages()
  }

  const conversationHistory = computed(() => {
    return messages.value.map(m => ({
      role: m.role,
      content: m.content
    }))
  })

  async function sendMessage(content: string) {
    if (!content.trim() || isLoading.value) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }
    messages.value.push(userMessage)

    isLoading.value = true
    error.value = null

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      }
      if (apiEnabled.value && apiKey.value) {
        headers['X-Api-Key'] = apiKey.value
      }

      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          mode: currentMode.value,
          level: currentLevel.value,
          message: content.trim(),
          conversation_history: conversationHistory.value.slice(0, -1)
        })
      })

      if (!response.ok) {
        throw new Error(`API 錯誤: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response,
        parsed: data.parsed_response,
        ttsSegments: data.tts_segments || [],
        timestamp: new Date()
      }
      messages.value.push(assistantMessage)

      return assistantMessage
    } catch (e) {
      error.value = e instanceof Error ? e.message : '發生錯誤'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function recordAnswer(
    question: string,
    userAnswer: string,
    isCorrect: boolean,
    grammarPoint?: string,
    explanation?: string
  ) {
    try {
      await fetch(`${API_BASE}/api/chat/record`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: currentMode.value,
          level: currentLevel.value,
          question,
          user_answer: userAnswer,
          is_correct: isCorrect,
          grammar_point: grammarPoint,
          explanation
        })
      })
    } catch (e) {
      console.error('記錄答案失敗:', e)
    }
  }

  function setMode(mode: 'grammar' | 'reading' | 'conversation') {
    currentMode.value = mode
    clearMessages()
  }

  function clearMessages() {
    messages.value = []
    error.value = null
  }

  return {
    messages,
    currentMode,
    currentLevel,
    isLoading,
    error,
    apiEnabled,
    apiKey,
    setApiEnabled,
    setApiKey,
    setLevel,
    sendMessage,
    recordAnswer,
    setMode,
    clearMessages
  }
}
