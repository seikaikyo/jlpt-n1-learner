import { ref, computed } from 'vue'

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
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const conversationHistory = computed(() => {
    return messages.value.map(m => ({
      role: m.role,
      content: m.content
    }))
  })

  async function sendMessage(content: string) {
    if (!content.trim() || isLoading.value) return

    // 添加用戶訊息
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
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: currentMode.value,
          message: content.trim(),
          conversation_history: conversationHistory.value.slice(0, -1)
        })
      })

      if (!response.ok) {
        throw new Error(`API 錯誤: ${response.status}`)
      }

      const data = await response.json()

      // 添加助手回覆
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
    isLoading,
    error,
    sendMessage,
    recordAnswer,
    setMode,
    clearMessages
  }
}
