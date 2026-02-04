import { ref, onUnmounted } from 'vue'

const isSpeaking = ref(false)
const currentMessageId = ref<string | null>(null)

let utteranceQueue: SpeechSynthesisUtterance[] = []

// 判斷文字是否包含日文假名
function containsJapanese(text: string): boolean {
  // 平假名: \u3040-\u309F, 片假名: \u30A0-\u30FF
  return /[\u3040-\u309F\u30A0-\u30FF]/.test(text)
}

// 取得日文女聲
function getJapaneseVoice(): SpeechSynthesisVoice | null {
  const voices = speechSynthesis.getVoices()
  const femaleVoice = voices.find(v =>
    v.lang.startsWith('ja') &&
    (v.name.includes('Kyoko') || v.name.includes('Haruka') || v.name.includes('Female') || v.name.includes('Google'))
  )
  return femaleVoice || voices.find(v => v.lang.startsWith('ja')) || null
}

// 取得中文女聲
function getChineseVoice(): SpeechSynthesisVoice | null {
  const voices = speechSynthesis.getVoices()
  // 優先找台灣中文，再找其他中文
  const twVoice = voices.find(v =>
    (v.lang === 'zh-TW' || v.lang.startsWith('zh-Hant')) &&
    (v.name.includes('Meijia') || v.name.includes('Female') || v.name.includes('Google'))
  )
  if (twVoice) return twVoice

  const cnVoice = voices.find(v =>
    v.lang.startsWith('zh') &&
    (v.name.includes('Tingting') || v.name.includes('Female') || v.name.includes('Google'))
  )
  return cnVoice || voices.find(v => v.lang.startsWith('zh')) || null
}

// 清理文字
function cleanText(text: string): string {
  return text
    .replace(/```[\s\S]*?```/g, '') // 移除 code block
    .replace(/\*\*(.*?)\*\*/g, '$1') // 移除粗體標記
    .replace(/\*(.*?)\*/g, '$1') // 移除斜體標記
    .replace(/#{1,6}\s/g, '') // 移除標題標記
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // 移除連結，保留文字
    .replace(/[「」『』【】〈〉《》（）\(\)\[\]{}・•―—–\-~～…。、，,\.!\?！？:：;；]/g, ' ') // 移除標點符號
    .replace(/\s+/g, ' ') // 合併多餘空白
    .trim()
}

// 把文字分成日文和中文段落
function splitByLanguage(text: string): Array<{ text: string; isJapanese: boolean }> {
  const segments: Array<{ text: string; isJapanese: boolean }> = []

  // 按句子或換行分割
  const sentences = text.split(/(?<=[\n。！？])|(?=[\n])/g).filter(s => s.trim())

  for (const sentence of sentences) {
    const cleaned = sentence.trim()
    if (!cleaned) continue

    const isJp = containsJapanese(cleaned)

    // 如果跟前一段同語言就合併
    const lastSegment = segments[segments.length - 1]
    if (segments.length > 0 && lastSegment && lastSegment.isJapanese === isJp) {
      lastSegment.text += ' ' + cleaned
    } else {
      segments.push({ text: cleaned, isJapanese: isJp })
    }
  }

  return segments
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

    const cleaned = cleanText(text)
    if (!cleaned) return

    // 分段並建立朗讀佇列
    const segments = splitByLanguage(cleaned)
    utteranceQueue = []

    for (let i = 0; i < segments.length; i++) {
      const segment = segments[i]!
      const segmentText = cleanText(segment.text)
      if (!segmentText) continue

      const utterance = new SpeechSynthesisUtterance(segmentText)
      utterance.lang = segment.isJapanese ? 'ja-JP' : 'zh-TW'
      utterance.rate = 1

      const voice = segment.isJapanese ? getJapaneseVoice() : getChineseVoice()
      if (voice) {
        utterance.voice = voice
      }

      if (i === 0) {
        utterance.onstart = () => {
          isSpeaking.value = true
          currentMessageId.value = messageId
        }
      }

      if (i === segments.length - 1) {
        utterance.onend = () => {
          isSpeaking.value = false
          currentMessageId.value = null
        }
        utterance.onerror = () => {
          isSpeaking.value = false
          currentMessageId.value = null
        }
      }

      utteranceQueue.push(utterance)
    }

    // 開始朗讀
    for (const utterance of utteranceQueue) {
      speechSynthesis.speak(utterance)
    }
  }

  // 停止朗讀
  function stop() {
    speechSynthesis.cancel()
    utteranceQueue = []
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
