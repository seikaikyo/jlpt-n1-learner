<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChat, type Message } from '../composables/useChat'
import { useSpeech } from '../composables/useSpeech'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import ProgressSpinner from 'primevue/progressspinner'
import Slider from 'primevue/slider'

interface Props {
  mode: 'grammar' | 'reading' | 'conversation'
}

const props = defineProps<Props>()

const { messages, isLoading, error, sendMessage, setMode } = useChat()
const { speakSegments, isPlayingMessage, speechRate } = useSpeech()

const inputText = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// 監聽模式變化
watch(() => props.mode, (newMode) => {
  setMode(newMode)
})

// 發送訊息
async function handleSend() {
  if (!inputText.value.trim() || isLoading.value) return

  const text = inputText.value
  inputText.value = ''

  await sendMessage(text)
  scrollToBottom()
}

// 處理鍵盤輸入
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

// 捲動到底部
async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 開始練習的提示訊息
function getStartPrompt(): string {
  switch (props.mode) {
    case 'grammar':
      return '請開始文法練習，出一題 N1 文法選擇題。'
    case 'reading':
      return '請開始讀解練習，給我一篇文章和選擇題。'
    case 'conversation':
      return '請開始聽解練習，給我一題聽力選擇題。'
    default:
      return '開始練習'
  }
}

// 格式化訊息內容
function formatContent(content: string): string {
  // 移除 JSON 區塊，只顯示文字部分
  let formatted = content.replace(/```json[\s\S]*?```/g, '')

  // 簡單的 markdown 轉換
  formatted = formatted
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')

  return formatted
}

// 解析 JSON 回覆中的選項
function getOptions(message: Message): string[] | null {
  if (message.parsed && Array.isArray(message.parsed.options)) {
    return message.parsed.options as string[]
  }
  return null
}
</script>

<template>
  <div class="chat-interface">
    <div class="chat-header">
      <h2 class="chat-title">
        {{ mode === 'grammar' ? '文法練習' : mode === 'reading' ? '讀解練習' : '聽解練習' }}
      </h2>
      <div class="header-controls">
        <div class="speed-control">
          <i class="pi pi-volume-up"></i>
          <Slider v-model="speechRate" :min="0.5" :max="1.5" :step="0.1" class="speed-slider" />
          <span class="speed-value">{{ speechRate.toFixed(1) }}x</span>
        </div>
        <span class="mode-badge">N1</span>
      </div>
    </div>

    <div ref="messagesContainer" class="messages-container">
      <!-- 空狀態 -->
      <div v-if="messages.length === 0" class="empty-chat">
        <i class="pi pi-comments"></i>
        <p>點擊下方按鈕開始練習</p>
        <Button
          :label="'開始' + (mode === 'grammar' ? '文法' : mode === 'reading' ? '讀解' : '聽解') + '練習'"
          icon="pi pi-play"
          @click="sendMessage(getStartPrompt())"
          :disabled="isLoading"
        />
      </div>

      <!-- 訊息列表 -->
      <div
        v-for="message in messages"
        :key="message.id"
        class="message"
        :class="message.role"
      >
        <div class="message-avatar">
          <i :class="message.role === 'user' ? 'pi pi-user' : 'pi pi-sparkles'"></i>
        </div>
        <div class="message-content">
          <div class="message-bubble">
            <div class="message-text" v-html="formatContent(message.content)"></div>
            <Button
              v-if="message.role === 'assistant' && message.ttsSegments && message.ttsSegments.length > 0"
              :icon="isPlayingMessage(message.id) ? 'pi pi-stop' : 'pi pi-volume-up'"
              severity="secondary"
              text
              rounded
              size="small"
              class="speak-btn"
              @click="speakSegments(message.ttsSegments, message.id)"
              v-tooltip.top="isPlayingMessage(message.id) ? '停止' : '朗讀'"
            />
          </div>

          <!-- 選項按鈕 -->
          <div v-if="message.role === 'assistant' && getOptions(message)" class="options-container">
            <Button
              v-for="(option, index) in getOptions(message)"
              :key="index"
              :label="option"
              severity="secondary"
              size="small"
              @click="sendMessage(option)"
              :disabled="isLoading"
            />
          </div>
        </div>
      </div>

      <!-- 載入中 -->
      <div v-if="isLoading" class="message assistant loading">
        <div class="message-avatar">
          <i class="pi pi-sparkles"></i>
        </div>
        <div class="message-content">
          <ProgressSpinner style="width: 24px; height: 24px;" strokeWidth="4" />
        </div>
      </div>
    </div>

    <!-- 錯誤提示 -->
    <div v-if="error" class="error-banner">
      <i class="pi pi-exclamation-triangle"></i>
      {{ error }}
    </div>

    <!-- 輸入區 -->
    <div class="input-area">
      <InputText
        v-model="inputText"
        placeholder="輸入你的回答..."
        class="chat-input"
        @keydown="handleKeydown"
        :disabled="isLoading"
      />
      <Button
        icon="pi pi-send"
        @click="handleSend"
        :disabled="!inputText.trim() || isLoading"
        :loading="isLoading"
      />
    </div>
  </div>
</template>

<style scoped>
.chat-interface {
  background: var(--surface-card);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
  min-height: 500px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.chat-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.speed-slider {
  width: 80px;
}

.speed-value {
  min-width: 32px;
  font-size: 0.75rem;
  font-weight: 500;
}

.mode-badge {
  background: var(--primary-color);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  text-align: center;
}

.empty-chat i {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-chat p {
  margin-bottom: 16px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #e0e7ff;
  color: var(--primary-color);
}

.message.assistant .message-avatar {
  background: #f0fdf4;
  color: #22c55e;
}

.message-content {
  max-width: 80%;
}

.message.user .message-content {
  text-align: right;
}

.message-bubble {
  display: flex;
  align-items: flex-start;
  gap: 4px;
}

.message.user .message-bubble {
  flex-direction: row-reverse;
}

.message-text {
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
}

.message.user .message-text {
  background: var(--primary-color);
  color: white;
  border-radius: 12px 12px 4px 12px;
}

.message.assistant .message-text {
  border-radius: 12px 12px 12px 4px;
}

.speak-btn {
  flex-shrink: 0;
  margin-top: 4px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.speak-btn:hover {
  opacity: 1;
}

.message.loading .message-content {
  display: flex;
  align-items: center;
  padding: 12px;
}

.options-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.error-banner {
  background: #fef2f2;
  color: #dc2626;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e2e8f0;
}

.chat-input {
  flex: 1;
}

:deep(.chat-input) {
  width: 100%;
}
</style>
