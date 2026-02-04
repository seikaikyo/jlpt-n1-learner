<script setup lang="ts">
interface Props {
  currentMode: 'grammar' | 'reading' | 'conversation'
}

defineProps<Props>()
const emit = defineEmits<{
  (e: 'select', mode: 'grammar' | 'reading' | 'conversation'): void
}>()

const modes = [
  { id: 'grammar', label: '文法練習', icon: 'pi-book', description: 'N1 文法點強化' },
  { id: 'reading', label: '讀解練習', icon: 'pi-file', description: '文章理解訓練' },
  { id: 'conversation', label: '聽解練習', icon: 'pi-headphones', description: '模擬聽力測驗' }
] as const
</script>

<template>
  <div class="mode-selector">
    <h3 class="section-title">練習模式</h3>
    <div class="mode-list">
      <button
        v-for="mode in modes"
        :key="mode.id"
        class="mode-item"
        :class="{ active: currentMode === mode.id }"
        @click="emit('select', mode.id)"
      >
        <i :class="['pi', mode.icon]"></i>
        <div class="mode-info">
          <span class="mode-label">{{ mode.label }}</span>
          <span class="mode-desc">{{ mode.description }}</span>
        </div>
      </button>
    </div>
  </div>
</template>

<style scoped>
.mode-selector {
  background: var(--surface-card);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
}

.mode-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mode-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.mode-item:hover {
  border-color: var(--primary-color);
  background: #f8fafc;
}

.mode-item.active {
  border-color: var(--primary-color);
  background: #eef2ff;
}

.mode-item i {
  font-size: 1.25rem;
  color: var(--primary-color);
  width: 24px;
}

.mode-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mode-label {
  font-weight: 500;
  color: var(--text-color);
}

.mode-desc {
  font-size: 0.75rem;
  color: var(--text-secondary);
}
</style>
