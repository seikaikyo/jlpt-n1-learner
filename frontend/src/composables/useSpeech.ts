import { ref, onUnmounted } from 'vue'
import type { TTSSegment } from './useChat'

const isSpeaking = ref(false)
const currentMessageId = ref<string | null>(null)
const speechRate = ref(0.9)

let utteranceQueue: SpeechSynthesisUtterance[] = []

// 取得日文女聲
function getJapaneseFemaleVoice(): SpeechSynthesisVoice | null {
  const voices = speechSynthesis.getVoices()
  // macOS: Kyoko, O-Ren / iOS: Kyoko / Google: ja-JP Female
  const femaleVoice = voices.find(v =>
    v.lang.startsWith('ja') &&
    (v.name.includes('Kyoko') || v.name.includes('O-Ren') || v.name.includes('Haruka') ||
     v.name.includes('Female') || (v.name.includes('Google') && !v.name.includes('Male')))
  )
  return femaleVoice || voices.find(v => v.lang.startsWith('ja')) || null
}

// 取得日文男聲
function getJapaneseMaleVoice(): SpeechSynthesisVoice | null {
  const voices = speechSynthesis.getVoices()
  // macOS: Otoya, Hattori / Google: ja-JP Male
  const maleVoice = voices.find(v =>
    v.lang.startsWith('ja') &&
    (v.name.includes('Otoya') || v.name.includes('Hattori') ||
     v.name.includes('Male') || v.name.includes('男'))
  )
  // 如果找不到男聲，用女聲但調低音調
  return maleVoice || null
}

// 取得中文女聲
function getChineseFemaleVoice(): SpeechSynthesisVoice | null {
  const voices = speechSynthesis.getVoices()
  const twVoice = voices.find(v =>
    (v.lang === 'zh-TW' || v.lang.startsWith('zh-Hant')) &&
    (v.name.includes('Meijia') || v.name.includes('Female') ||
     (v.name.includes('Google') && !v.name.includes('Male')))
  )
  if (twVoice) return twVoice

  const cnVoice = voices.find(v =>
    v.lang.startsWith('zh') &&
    (v.name.includes('Tingting') || v.name.includes('Female'))
  )
  return cnVoice || voices.find(v => v.lang.startsWith('zh')) || null
}

// 取得中文男聲
function getChineseMaleVoice(): SpeechSynthesisVoice | null {
  const voices = speechSynthesis.getVoices()
  const maleVoice = voices.find(v =>
    v.lang.startsWith('zh') &&
    (v.name.includes('Sinji') || v.name.includes('Male') || v.name.includes('男'))
  )
  return maleVoice || null
}

// 建立停頓用的 utterance
function createPauseUtterance(type: 'short' | 'long' | 'speaker'): SpeechSynthesisUtterance {
  const pause = new SpeechSynthesisUtterance('　')
  pause.volume = 0

  switch (type) {
    case 'short':   // 逗號：短換氣
      pause.rate = 2
      break
    case 'long':    // 句號：兩倍時間
      pause.rate = 1
      break
    case 'speaker': // 換人說話：最長
      pause.rate = 0.5
      break
  }

  return pause
}

export function useSpeech() {
  // 使用後端解析好的 TTS segments 播放
  function speakSegments(segments: TTSSegment[], messageId: string) {
    if (isSpeaking.value && currentMessageId.value === messageId) {
      stop()
      return
    }

    stop()

    if (!segments || segments.length === 0) return

    utteranceQueue = []
    let isFirst = true

    for (const segment of segments) {
      if (!segment.text) continue

      // 如果有 pause_before，先加停頓
      if (segment.pause_before === 'speaker') {
        utteranceQueue.push(createPauseUtterance('speaker'))
      }

      // 建立語音
      const utterance = new SpeechSynthesisUtterance(segment.text)
      const isMale = segment.voice === 'male'

      if (segment.lang === 'ja') {
        utterance.lang = 'ja-JP'
        if (isMale) {
          const voice = getJapaneseMaleVoice()
          if (voice) {
            utterance.voice = voice
          } else {
            // 沒有男聲時用女聲但降低音調
            const femaleVoice = getJapaneseFemaleVoice()
            if (femaleVoice) utterance.voice = femaleVoice
            utterance.pitch = 0.7
          }
        } else {
          const voice = getJapaneseFemaleVoice()
          if (voice) utterance.voice = voice
        }
      } else {
        utterance.lang = 'zh-TW'
        if (isMale) {
          const voice = getChineseMaleVoice()
          if (voice) {
            utterance.voice = voice
          } else {
            const femaleVoice = getChineseFemaleVoice()
            if (femaleVoice) utterance.voice = femaleVoice
            utterance.pitch = 0.7
          }
        } else {
          const voice = getChineseFemaleVoice()
          if (voice) utterance.voice = voice
        }
      }

      utterance.rate = speechRate.value

      // 第一個 utterance 設定 onstart
      if (isFirst) {
        utterance.onstart = () => {
          isSpeaking.value = true
          currentMessageId.value = messageId
        }
        isFirst = false
      }

      utteranceQueue.push(utterance)

      // 根據 pause_after 加入停頓
      if (segment.pause_after === 'short') {
        utteranceQueue.push(createPauseUtterance('short'))
      } else if (segment.pause_after === 'long') {
        utteranceQueue.push(createPauseUtterance('long'))
      }
    }

    // 最後一個設定結束事件
    if (utteranceQueue.length > 0) {
      const last = utteranceQueue[utteranceQueue.length - 1]!
      last.onend = () => {
        isSpeaking.value = false
        currentMessageId.value = null
      }
      last.onerror = () => {
        isSpeaking.value = false
        currentMessageId.value = null
      }
    }

    // 播放
    for (const u of utteranceQueue) {
      speechSynthesis.speak(u)
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
    speakSegments,
    stop,
    isPlayingMessage
  }
}
