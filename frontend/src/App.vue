<script setup lang="ts">
import { ref } from 'vue'
import Toast from 'primevue/toast'
import ModeSelector from './components/ModeSelector.vue'
import ProgressPanel from './components/ProgressPanel.vue'
import ChatInterface from './components/ChatInterface.vue'

const currentMode = ref<'grammar' | 'reading' | 'conversation'>('grammar')

function handleModeSelect(mode: 'grammar' | 'reading' | 'conversation') {
  currentMode.value = mode
}
</script>

<template>
  <Toast />
  <div class="app-container">
    <header class="app-header">
      <h1>JLPT N1 學習系統</h1>
      <p>AI 驅動的適應性日語學習</p>
    </header>

    <main class="main-content">
      <aside class="sidebar">
        <ModeSelector
          :current-mode="currentMode"
          @select="handleModeSelect"
        />
        <ProgressPanel />
      </aside>

      <section class="chat-section">
        <ChatInterface :mode="currentMode" />
      </section>
    </main>
  </div>
</template>

<style scoped>
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
}
</style>
