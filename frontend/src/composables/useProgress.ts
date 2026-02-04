import { ref, onMounted } from 'vue'

export interface ProgressStats {
  total_practices: number
  overall_accuracy: number
  by_mode: Record<string, { count: number; accuracy: number }>
  weak_grammar_count: number
}

const API_BASE = 'http://localhost:8002'

export function useProgress() {
  const stats = ref<ProgressStats | null>(null)
  const weakAreas = ref<string[]>([])
  const isLoading = ref(false)

  async function fetchProgress() {
    isLoading.value = true
    try {
      const response = await fetch(`${API_BASE}/api/progress`)
      if (!response.ok) throw new Error('Failed to fetch progress')

      const data = await response.json()
      weakAreas.value = data.data.weak_areas || []
    } catch (e) {
      console.error('取得進度失敗:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchSummary() {
    try {
      const response = await fetch(`${API_BASE}/api/progress/summary`)
      if (!response.ok) throw new Error('Failed to fetch summary')

      const data = await response.json()
      stats.value = data.data
    } catch (e) {
      console.error('取得統計失敗:', e)
    }
  }

  function refresh() {
    fetchProgress()
    fetchSummary()
  }

  onMounted(() => {
    refresh()
  })

  return {
    stats,
    weakAreas,
    isLoading,
    refresh
  }
}
