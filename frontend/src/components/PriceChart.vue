<template>
  <div class="chart-wrap">
    <div class="chart-header">
      <span class="chart-title">價格走勢</span>
      <div class="period-tabs">
        <button
          v-for="p in periods"
          :key="p.value"
          class="period-btn"
          :class="{ active: period === p.value }"
          @click="changePeriod(p.value)"
        >{{ p.label }}</button>
      </div>
    </div>
    <div class="chart-container">
      <canvas ref="canvasEl"></canvas>
      <div v-if="loading" class="overlay">載入走勢圖...</div>
      <div v-if="hasError && !loading" class="overlay error">
        ⚠️ 無法載入資料
        <button class="retry-btn" @click="loadChart">重試</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import {
  Chart, LineController, LineElement, PointElement,
  LinearScale, Filler, Tooltip, CategoryScale, BarController, BarElement,
} from 'chart.js'
import {
  CandlestickController, CandlestickElement,
} from 'chartjs-chart-financial'
import axios from 'axios'

Chart.register(
  LineController, LineElement, PointElement,
  LinearScale, Filler, Tooltip, CategoryScale,
  BarController, BarElement,
  CandlestickController, CandlestickElement,
)

const props = defineProps<{
  symbol: string
  chartType?: 'area' | 'line' | 'candle'
}>()

const canvasEl = ref<HTMLCanvasElement | null>(null)
const loading = ref(true)
const hasError = ref(false)
const period = ref('3mo')

const periods = [
  { label: '1M', value: '1mo' },
  { label: '3M', value: '3mo' },
  { label: '6M', value: '6mo' },
  { label: '1Y', value: '1y' },
]

let chart: Chart | null = null

function buildConfig(type: string, labels: string[], rawData: any[]) {
  if (type === 'candle') {
    const candleData = rawData.map((d: any, i: number) => ({
      x: i,
      o: d.open, h: d.high, l: d.low, c: d.close,
    }))
    return {
      type: 'candlestick' as const,
      data: {
        labels,
        datasets: [{
          label: props.symbol,
          data: candleData,
          color: {
            up: '#4caf50',
            down: '#f44336',
            unchanged: '#888',
          },
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: { legend: { display: false }, tooltip: candleTooltip() },
        scales: candleScales(),
      },
    }
  }

  const values = rawData.map((d: any) => d.close)
  return {
    type: 'line' as const,
    data: {
      labels,
      datasets: [{
        data: values,
        borderColor: '#4361ee',
        backgroundColor: type === 'area' ? 'rgba(67,97,238,0.15)' : 'transparent',
        borderWidth: type === 'area' ? 2 : 1.5,
        pointRadius: 0,
        fill: type === 'area',
        tension: 0.2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      plugins: { legend: { display: false }, tooltip: lineTooltip() },
      scales: lineScales(),
    },
  }
}

function lineTooltip() {
  return {
    mode: 'index' as const,
    intersect: false,
    backgroundColor: '#1e1e2e',
    titleColor: '#aaa',
    bodyColor: '#fff',
    borderColor: '#2a2a3e',
    borderWidth: 1,
    callbacks: { label: (ctx: any) => ` ${ctx.parsed.y.toFixed(2)}` },
  }
}

function candleTooltip() {
  return {
    backgroundColor: '#1e1e2e',
    titleColor: '#aaa',
    bodyColor: '#fff',
    borderColor: '#2a2a3e',
    borderWidth: 1,
  }
}

function lineScales() {
  return {
    x: {
      ticks: { color: '#555', maxTicksLimit: 6, maxRotation: 0 },
      grid: { color: '#1e1e2e' },
    },
    y: {
      ticks: { color: '#555' },
      grid: { color: '#1e1e2e' },
      position: 'right' as const,
    },
  }
}

function candleScales() {
  return {
    x: {
      type: 'category' as const,
      ticks: { color: '#555', maxTicksLimit: 6, maxRotation: 0 },
      grid: { color: '#1e1e2e' },
    },
    y: {
      ticks: { color: '#555' },
      grid: { color: '#1e1e2e' },
      position: 'right' as const,
    },
  }
}

async function loadChart() {
  loading.value = true
  hasError.value = false
  try {
    const { data } = await axios.get(
      `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/api/history/${props.symbol}?period=${period.value}`,
      { timeout: 15000 }
    )
    if (!data?.length) { hasError.value = true; return }

    const sorted = [...data].sort((a: any, b: any) => a.date > b.date ? 1 : -1)
    const labels = sorted.map((d: any) => d.date)
    const type = props.chartType ?? 'area'

    if (chart) {
      chart.destroy()
      chart = null
      await nextTick()
    }
    if (canvasEl.value) {
      chart = new Chart(canvasEl.value, buildConfig(type, labels, sorted) as any)
    }
  } catch (e) {
    console.error('chart error', e)
    hasError.value = true
  } finally {
    loading.value = false
  }
}

function changePeriod(p: string) {
  period.value = p
  loadChart()
}

onMounted(async () => {
  await nextTick()
  loadChart()
})

onUnmounted(() => { chart?.destroy(); chart = null })

watch(() => props.symbol, () => loadChart())
watch(() => props.chartType, () => loadChart())
</script>

<style scoped>
.chart-wrap {
  background: #0a0a14;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #1e1e2e;
}
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.chart-title { font-size: 13px; color: #555; text-transform: uppercase; letter-spacing: 1px; }
.period-tabs { display: flex; gap: 4px; }
.period-btn {
  background: transparent; border: 1px solid #1e1e2e; color: #555;
  border-radius: 6px; padding: 3px 10px; font-size: 12px;
  cursor: pointer; transition: all 0.15s;
}
.period-btn:hover { background: #1e1e2e; color: #aaa; }
.period-btn.active { background: #4361ee; border-color: #4361ee; color: #fff; }

.chart-container { position: relative; height: 260px; }
canvas { width: 100% !important; height: 100% !important; }

.overlay {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center; gap: 12px;
  color: #555; font-size: 13px;
  background: rgba(10,10,20,0.85); border-radius: 8px;
}
.overlay.error { color: #f44336; }
.retry-btn {
  background: #1e1e2e; border: 1px solid #2a2a3e; color: #aaa;
  border-radius: 6px; padding: 4px 12px; cursor: pointer; font-size: 12px;
}
.retry-btn:hover { color: #fff; background: #2a2a3e; }
</style>
