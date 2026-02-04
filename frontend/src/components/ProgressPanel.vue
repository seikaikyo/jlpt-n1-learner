<script setup lang="ts">
import { useProgress } from '../composables/useProgress'
import ProgressBar from 'primevue/progressbar'

const { stats, weakAreas, refresh } = useProgress()

const modeLabels: Record<string, string> = {
  grammar: '文法',
  reading: '讀解',
  vocabulary: '語彙',
  conversation: '會話'
}
</script>

<template>
  <div class="progress-panel">
    <div class="panel-header">
      <h3 class="section-title">學習進度</h3>
      <button class="refresh-btn" @click="refresh" title="重新整理">
        <i class="pi pi-refresh"></i>
      </button>
    </div>

    <template v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_practices }}</div>
        <div class="stat-label">總練習次數</div>
      </div>

      <div class="stat-card">
        <div class="stat-value">{{ (stats.overall_accuracy * 100).toFixed(0) }}%</div>
        <div class="stat-label">整體正確率</div>
        <ProgressBar
          :value="stats.overall_accuracy * 100"
          :showValue="false"
          style="height: 6px; margin-top: 8px;"
        />
      </div>

      <div class="mode-stats">
        <h4 class="subsection-title">各模式統計</h4>
        <div
          v-for="(data, mode) in stats.by_mode"
          :key="mode"
          class="mode-stat-item"
        >
          <span class="mode-name">{{ modeLabels[mode] || mode }}</span>
          <span class="mode-count">{{ data.count }} 題</span>
          <span class="mode-accuracy">{{ (data.accuracy * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="empty-state">
        <i class="pi pi-chart-bar"></i>
        <p>開始練習後將顯示統計</p>
      </div>
    </template>

    <div v-if="weakAreas.length" class="weak-areas">
      <h4 class="subsection-title">需加強項目</h4>
      <ul class="weak-list">
        <li v-for="area in weakAreas" :key="area">{{ area }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.progress-panel {
  background: var(--surface-card);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.refresh-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.refresh-btn:hover {
  background: #f1f5f9;
  color: var(--primary-color);
}

.stat-card {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary-color);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.subsection-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 16px 0 8px;
}

.mode-stats {
  margin-top: 16px;
}

.mode-stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
}

.mode-stat-item:last-child {
  border-bottom: none;
}

.mode-name {
  color: var(--text-color);
}

.mode-count {
  color: var(--text-secondary);
}

.mode-accuracy {
  font-weight: 500;
  color: var(--primary-color);
}

.empty-state {
  text-align: center;
  padding: 32px 16px;
  color: var(--text-secondary);
}

.empty-state i {
  font-size: 2rem;
  margin-bottom: 8px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 0.875rem;
}

.weak-areas {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.weak-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.weak-list li {
  padding: 6px 0;
  font-size: 0.875rem;
  color: #ef4444;
}

.weak-list li::before {
  content: '!';
  display: inline-block;
  width: 16px;
  height: 16px;
  background: #fef2f2;
  border-radius: 50%;
  text-align: center;
  line-height: 16px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-right: 8px;
}
</style>
