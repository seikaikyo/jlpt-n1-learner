import { ref, onUnmounted } from 'vue'

const isSpeaking = ref(false)
const currentMessageId = ref<string | null>(null)

let utterance: SpeechSynthesisUtterance | null = null

// 取得日文女聲
function getJapaneseVoice(): SpeechSynthesisVoice | null {
  const voices = speechSynthesis.getVoices()
  // 優先找女聲：Kyoko (macOS), Google 日本語 (Chrome), Haruka (Windows)
  const femaleVoice = voices.find(v =>
    v.lang.startsWith('ja') &&
    (v.name.includes('Kyoko') || v.name.includes('Haruka') || v.name.includes('Female') || v.name.includes('Google'))
  )
  // 找不到就用任意日文語音
  return femaleVoice || voices.find(v => v.lang.startsWith('ja')) || null
}

export function useSpeech() {
  // 朗讀文字
  function speak(text: string, messageId: string) {
    // 如果正在播放同一則，停止
    if (isSpeaking.value && currentMessageId.value === messageId) {
      stop()
      return
    }

    // 停止任何進行中的朗讀
    stop()

    // 清理文字：移除 markdown 和特殊符號
    const cleanText = text
      .replace(/```[\s\S]*?```/g, '') // 移除 code block
      .replace(/\*\*(.*?)\*\*/g, '$1') // 移除粗體標記
      .replace(/\*(.*?)\*/g, '$1') // 移除斜體標記
      .replace(/#{1,6}\s/g, '') // 移除標題標記
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // 移除連結，保留文字
      .trim()

    if (!cleanText) return

    utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.lang = 'ja-JP'
    utterance.rate = 1

    // 設定女聲
    const voice = getJapaneseVoice()
    if (voice) {
      utterance.voice = voice
    }

    utterance.onstart = () => {
      isSpeaking.value = true
      currentMessageId.value = messageId
    }

    utterance.onend = () => {
      isSpeaking.value = false
      currentMessageId.value = null
    }

    utterance.onerror = () => {
      isSpeaking.value = false
      currentMessageId.value = null
    }

    speechSynthesis.speak(utterance)
  }

  // 停止朗讀
  function stop() {
    speechSynthesis.cancel()
    isSpeaking.value = false
    currentMessageId.value = null
  }

  // 檢查是否正在播放特定訊息
  function isPlayingMessage(messageId: string): boolean {
    return isSpeaking.value && currentMessageId.value === messageId
  }

  // 組件卸載時清理
  onUnmounted(() => {
    stop()
  })

  return {
    isSpeaking,
    currentMessageId,
    speak,
    stop,
    isPlayingMessage
  }
}
