<script setup lang="ts">
import { ref } from 'vue'
import Toast from 'primevue/toast'
import Button from 'primevue/button'
import Select from 'primevue/select'
import ToggleSwitch from 'primevue/toggleswitch'
import Password from 'primevue/password'
import ModeSelector from './components/ModeSelector.vue'
import ProgressPanel from './components/ProgressPanel.vue'
import ChatInterface from './components/ChatInterface.vue'
import { useChat, type JlptLevel } from './composables/useChat'

const chat = useChat()
const currentMode = ref<'grammar' | 'reading' | 'conversation'>('grammar')
const showSettings = ref(false)

const levelOptions = [
  { label: 'N5（入門）', value: 'n5' },
  { label: 'N4（初級）', value: 'n4' },
  { label: 'N3（中級）', value: 'n3' },
  { label: 'N2（中上級）', value: 'n2' },
  { label: 'N1（上級）', value: 'n1' },
]

function handleModeSelect(mode: 'grammar' | 'reading' | 'conversation') {
  currentMode.value = mode
}

function handleLevelChange(value: JlptLevel) {
  chat.setLevel(value)
}
</script>

<template>
  <Toast />
  <div class="app-container">
    <header class="app-header">
      <div>
        <h1>JLPT 學習系統</h1>
        <p>AI 驅動的適應性日語學習</p>
      </div>
      <div class="header-actions">
        <Select
          :modelValue="chat.currentLevel.value"
          :options="levelOptions"
          optionLabel="label"
          optionValue="value"
          class="level-select"
          @update:modelValue="handleLevelChange"
        />
        <Button
          icon="pi pi-cog"
          severity="secondary"
          text
          rounded
          title="設定"
          @click="showSettings = !showSettings"
        />
      </div>
    </header>

    <!-- 設定面板 -->
    <div v-if="showSettings" class="settings-panel">
      <div class="setting-row">
        <label for="api-toggle">AI 模式</label>
        <ToggleSwitch
          :modelValue="chat.apiEnabled.value"
          inputId="api-toggle"
          @update:modelValue="chat.setApiEnabled($event)"
        />
        <span class="setting-hint">{{ chat.apiEnabled.value ? '開啟' : '關閉 (離線題庫)' }}</span>
      </div>
      <div v-if="chat.apiEnabled.value" class="setting-row">
        <label for="api-key">API Key</label>
        <Password
          :modelValue="chat.apiKey.value"
          inputId="api-key"
          placeholder="sk-ant-..."
          :feedback="false"
          toggleMask
          class="api-key-input"
          @update:modelValue="chat.setApiKey($event)"
        />
      </div>
      <p class="setting-hint">
        {{ chat.apiEnabled.value && chat.apiKey.value ? 'AI 自適應出題模式' : '離線題庫練習模式（不需 API）' }}
      </p>
    </div>

    <main class="main-content">
      <aside class="sidebar">
        <ModeSelector
          :current-mode="currentMode"
          :current-level="chat.currentLevel.value"
          @select="handleModeSelect"
        />
        <ProgressPanel />
      </aside>

      <section class="chat-section">
        <ChatInterface :mode="currentMode" :level="chat.currentLevel.value" />
      </section>
    </main>
  </div>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.level-select {
  width: 160px;
}

.settings-panel {
  padding: 12px 16px;
  border-bottom: 1px solid var(--surface-border, #e2e8f0);
  background: var(--surface-ground, #f8fafc);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-row label {
  font-size: 13px;
  font-weight: 500;
  min-width: 64px;
}

.setting-hint {
  font-size: 12px;
  color: var(--text-color-secondary, #64748b);
}

.api-key-input {
  flex: 1;
  max-width: 280px;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-section {
  min-width: 0;
}

@media (max-width: 768px) {
  .sidebar {
    order: 2;
  }

  .chat-section {
    order: 1;
  }

  .level-select {
    width: 120px;
  }
}
</style>
