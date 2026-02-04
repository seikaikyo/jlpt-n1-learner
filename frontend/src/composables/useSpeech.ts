import { ref, onUnmounted } from 'vue'

const isSpeaking = ref(false)
const currentMessageId = ref<string | null>(null)
const speechRate = ref(0.9) // 預設語速

let utteranceQueue: SpeechSynthesisUtterance[] = []

// 判斷字符是否為假名
function isKana(char: string): boolean {
  const code = char.charCodeAt(0)
  // 平假名: 3040-309F, 片假名: 30A0-30FF, 長音符: 30FC
  return (code >= 0x3040 && code <= 0x309F) ||
         (code >= 0x30A0 && code <= 0x30FF)
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

// 清理 markdown 格式
function cleanMarkdown(text: string): string {
  return text
    .replace(/```[\s\S]*?```/g, '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/#{1,6}\s/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
}

// 只保留中日文字符，其他全部移除
function removePunctuation(text: string): string {
  // 只保留：平假名、片假名、漢字、空格
  return text
    .replace(/[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3400-\u4DBF\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

// 把文字分成日文和中文段落
// 關鍵：看一段文字裡有沒有假名，有假名就是日文
function splitByLanguage(text: string): Array<{ text: string; isJapanese: boolean }> {
  const segments: Array<{ text: string; isJapanese: boolean }> = []

  // 按換行和句號分割
  const sentences = text.split(/[\n。]+/).filter(s => s.trim())

  for (const sentence of sentences) {
    const trimmed = sentence.trim()
    if (!trimmed) continue

    // 檢查這個句子有沒有假名
    let hasKana = false
    for (const char of trimmed) {
      if (isKana(char)) {
        hasKana = true
        break
      }
    }

    // 有假名 = 日文，沒假名 = 中文
    const lastSegment = segments[segments.length - 1]
    if (lastSegment && lastSegment.isJapanese === hasKana) {
      lastSegment.text += ' ' + trimmed
    } else {
      segments.push({ text: trimmed, isJapanese: hasKana })
    }
  }

  return segments
}

export function useSpeech() {
  function speak(text: string, messageId: string) {
    if (isSpeaking.value && currentMessageId.value === messageId) {
      stop()
      return
    }

    stop()

    const cleaned = cleanMarkdown(text)
    if (!cleaned.trim()) return

    const segments = splitByLanguage(cleaned)
    utteranceQueue = []

    const validSegments: Array<{ text: string; isJapanese: boolean }> = []

    for (const segment of segments) {
      const segmentText = removePunctuation(segment.text)
      if (segmentText) {
        validSegments.push({ text: segmentText, isJapanese: segment.isJapanese })
      }
    }

    if (validSegments.length === 0) return

    for (let i = 0; i < validSegments.length; i++) {
      const segment = validSegments[i]!
      const utterance = new SpeechSynthesisUtterance(segment.text)

      if (segment.isJapanese) {
        utterance.lang = 'ja-JP'
        const voice = getJapaneseVoice()
        if (voice) utterance.voice = voice
      } else {
        utterance.lang = 'zh-TW'
        const voice = getChineseVoice()
        if (voice) utterance.voice = voice
      }

      utterance.rate = speechRate.value

      if (i === 0) {
        utterance.onstart = () => {
          isSpeaking.value = true
          currentMessageId.value = messageId
        }
      }

      if (i === validSegments.length - 1) {
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

    for (const utterance of utteranceQueue) {
      speechSynthesis.speak(utterance)
    }
  }

  function stop() {
    speechSynthesis.cancel()
    utteranceQueue = []
    isSpeaking.value = false
    currentMessageId.value = null
  }

  function isPlayingMessage(messageId: string): boolean {
    return isSpeaking.value && currentMessageId.value === messageId
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isSpeaking,
    currentMessageId,
    speechRate,
    speak,
    stop,
    isPlayingMessage
  }
}
