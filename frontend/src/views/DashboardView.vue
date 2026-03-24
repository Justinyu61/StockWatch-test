<template>
  <div class="app">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <span class="logo">📈 StockWatch</span>
        <span class="ws-status" :class="{ connected: store.wsConnected }">
          {{ store.wsConnected ? '● 即時連線' : '○ 連線中...' }}
        </span>
        <span class="update-time" v-if="lastUpdate">更新 {{ lastUpdate }}</span>
      </div>
      <div class="header-right">
        <button class="refresh-btn" @click="refresh" :disabled="refreshing">
          {{ refreshing ? '更新中...' : '⟳ 立即更新' }}
        </button>
        <button class="settings-btn" @click="showSettings = true" title="自選股設定">
          ☰
        </button>
      </div>
    </header>

    <!-- 設定抽屜 -->
    <div class="drawer-overlay" v-if="showSettings" @click="showSettings = false"></div>
    <div class="settings-drawer" :class="{ open: showSettings }">
      <div class="drawer-header">
        <h3>⚙️ 自選股設定</h3>
        <button class="icon-btn" @click="showSettings = false">✕</button>
      </div>
      <div class="drawer-body">
        <!-- 圖表樣式選擇 -->
        <div class="drawer-section">
          <div class="drawer-section-label">圖表樣式</div>
          <div class="chart-type-row">
            <button
              class="chart-type-btn"
              :class="{ active: store.chartType === 'area' }"
              @click="store.chartType = 'area'"
            >曲線</button>
            <button
              class="chart-type-btn"
              :class="{ active: store.chartType === 'line' }"
              @click="store.chartType = 'line'"
            >折線</button>
            <button
              class="chart-type-btn"
              :class="{ active: store.chartType === 'candle' }"
              @click="store.chartType = 'candle'"
            >K線</button>
          </div>
        </div>
        <p class="drawer-hint">台股格式：2330.TW　美股格式：AAPL</p>
        <div class="add-row">
          <input
            v-model="newSymbol"
            class="add-input"
            placeholder="股票代碼，如 NVDA"
            @keyup.enter="addStock"
          />
          <input
            v-model="newName"
            class="add-input"
            placeholder="名稱，如 NVIDIA"
            @keyup.enter="addStock"
          />
          <button class="add-btn" @click="addStock">新增</button>
        </div>
        <div class="stock-list">
          <div
            v-for="(item, i) in store.watchlist"
            :key="item.symbol"
            class="stock-row"
          >
            <span class="stock-row-name">{{ item.name }}</span>
            <span class="stock-row-symbol">{{ item.symbol }}</span>
            <button class="remove-btn" @click="removeStock(i)">✕</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Layout -->
    <div class="main">
      <!-- 左：股票卡片清單 -->
      <div class="sidebar">
        <StockCard
          v-for="item in store.watchlist"
          :key="item.symbol"
          :symbol="item.symbol"
          :name="item.name"
          :quote="store.quotes[item.symbol]"
          :active="selected === item.symbol"
          @click="selectStock(item.symbol)"
        />
      </div>

      <!-- 右：詳細資訊 -->
      <div class="detail">
        <div v-if="!selected" class="empty-state">
          <div class="empty-icon">📊</div>
          <p>點擊左側股票</p>
          <p class="hint">查看走勢圖與技術指標</p>
        </div>
        <div v-else class="detail-content">
          <div class="detail-header">
            <div>
              <h2>{{ selectedStock?.name }}
                <span class="symbol-tag">{{ selected }}</span>
              </h2>
              <div v-if="store.quotes[selected]" class="detail-price-row">
                <span class="detail-price">{{ store.quotes[selected].price.toFixed(2) }}</span>
                <span class="detail-change"
                  :class="store.quotes[selected].change_pct >= 0 ? 'up' : 'down'">
                  {{ store.quotes[selected].change_pct >= 0 ? '▲' : '▼' }}
                  {{ Math.abs(store.quotes[selected].change_pct).toFixed(2) }}%
                </span>
              </div>
            </div>
            <button class="icon-btn" @click="closeDetail">✕</button>
          </div>

          <!-- 走勢圖 + 技術指標並排 -->
          <div class="chart-indicator-row">
            <div class="chart-col">
              <PriceChart :symbol="selected" :chart-type="store.chartType" />
            </div>
            <div class="indicator-col">
              <IndicatorPanel :symbol="selected" :aside="true" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useStockStore } from '@/stores/stock'
import StockCard from '@/components/StockCard.vue'
import IndicatorPanel from '@/components/IndicatorPanel.vue'
import PriceChart from '@/components/PriceChart.vue'

const store = useStockStore()
const selected = ref<string | null>(null)
const refreshing = ref(false)
const lastUpdate = ref('')
const showSettings = ref(false)
const newSymbol = ref('')
const newName = ref('')

const selectedStock = computed(() =>
  store.watchlist.find(s => s.symbol === selected.value)
)

function selectStock(symbol: string) {
  selected.value = selected.value === symbol ? null : symbol
  if (selected.value) store.fetchIndicators(symbol)
}

function closeDetail() {
  selected.value = null
}

async function refresh() {
  refreshing.value = true
  try {
    await axios.post(`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/api/refresh`)
    lastUpdate.value = new Date().toLocaleTimeString('zh-TW', {
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    })
  } finally {
    setTimeout(() => { refreshing.value = false }, 2000)
  }
}

async function addStock() {
  const symbol = newSymbol.value.trim().toUpperCase()
  const name = newName.value.trim() || symbol
  if (!symbol) return
  if (store.watchlist.find(s => s.symbol === symbol)) return
  try {
    await axios.post(`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/api/watchlist`, { symbol, name })
    store.watchlist.push({ symbol, name, market: symbol.endsWith('.TW') ? 'TW' : 'US' })
    newSymbol.value = ''
    newName.value = ''
  } catch { /* 409 = 已存在，忽略 */ }
}

async function removeStock(index: number) {
  const removed = store.watchlist[index]
  try {
    await axios.delete(`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/api/watchlist/${removed.symbol}`)
    store.watchlist.splice(index, 1)
    if (selected.value === removed.symbol) selected.value = null
  } catch { /* 忽略 */ }
}

onMounted(async () => {
  await store.fetchWatchlist()
  store.connectWebSocket()
  await refresh()
})
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0a0a10;
  color: #e0e0e0;
  overflow: hidden;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 24px;
  border-bottom: 1px solid #1e1e2e;
  flex-shrink: 0;
  z-index: 10;
}
.header-left { display: flex; align-items: center; gap: 14px; }
.header-right { display: flex; align-items: center; gap: 10px; }
.logo { font-size: 20px; font-weight: 700; color: #fff; }
.ws-status { font-size: 13px; color: #555; }
.ws-status.connected { color: #4caf50; }
.update-time { font-size: 12px; color: #444; }

.refresh-btn {
  background: #1e1e2e; color: #aaa;
  border: 1px solid #2a2a3e; border-radius: 8px;
  padding: 6px 14px; font-size: 13px; cursor: pointer;
  transition: all 0.2s;
}
.refresh-btn:hover:not(:disabled) { background: #2a2a3e; color: #fff; }
.refresh-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.settings-btn {
  background: #1e1e2e; color: #aaa;
  border: 1px solid #2a2a3e; border-radius: 8px;
  width: 38px; height: 38px; font-size: 18px;
  cursor: pointer; transition: all 0.2s;
}
.settings-btn:hover { background: #2a2a3e; color: #fff; }

/* 設定抽屜 */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 90;
}

.settings-drawer {
  position: fixed;
  top: 0;
  left: -360px;
  width: 340px;
  height: 100vh;
  background: #0e0e1a;
  border-right: 1px solid #2a2a3e;
  z-index: 100;
  display: flex;
  flex-direction: column;
  transition: left 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.settings-drawer.open { left: 0; }

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 16px;
  border-bottom: 1px solid #1e1e2e;
  flex-shrink: 0;
}
.drawer-header h3 { color: #fff; font-size: 16px; }

.drawer-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  scrollbar-width: none;
}
.drawer-body::-webkit-scrollbar { display: none; }

.drawer-hint { font-size: 12px; color: #555; margin-bottom: 16px; }

.add-row { display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; }
.add-input {
  width: 100%;
  background: #0a0a14; border: 1px solid #2a2a3e;
  color: #fff; border-radius: 8px; padding: 8px 12px; font-size: 14px;
}
.add-input:focus { outline: none; border-color: #4361ee; }
.add-btn {
  background: #4361ee; color: #fff; border: none;
  border-radius: 8px; padding: 9px 16px; cursor: pointer;
  font-size: 14px;
}
.add-btn:hover { background: #3451de; }

.stock-list { display: flex; flex-direction: column; gap: 8px; }
.stock-row {
  display: flex; align-items: center; gap: 12px;
  background: #0a0a14; border: 1px solid #1e1e2e;
  border-radius: 8px; padding: 10px 14px;
}
.stock-row-name { flex: 1; color: #fff; font-size: 14px; }
.stock-row-symbol { color: #555; font-size: 13px; }

/* Main Layout */
.main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左側卡片列表 */
.sidebar {
  width: 290px;
  flex-shrink: 0;
  overflow-y: auto;
  padding: 14px;
  border-right: 1px solid #1e1e2e;
  display: flex;
  flex-direction: column;
  gap: 10px;
  scrollbar-width: none;
}
.sidebar::-webkit-scrollbar { display: none; }

/* 右側詳細 */
.detail {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scrollbar-width: none;
}
.detail::-webkit-scrollbar { display: none; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 8px;
  color: #333;
}
.empty-icon { font-size: 48px; margin-bottom: 8px; }
.empty-state p { font-size: 16px; color: #444; }
.empty-state .hint { font-size: 13px; color: #333; }

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
h2 { font-size: 22px; color: #fff; display: flex; align-items: center; gap: 10px; }
.symbol-tag {
  font-size: 13px; background: #1e1e2e;
  color: #666; padding: 2px 8px; border-radius: 6px; font-weight: 400;
}
.detail-price-row { display: flex; align-items: baseline; gap: 10px; margin-top: 4px; }
.detail-price { font-size: 32px; font-weight: 700; color: #fff; }
.detail-change { font-size: 16px; font-weight: 600; }
.detail-change.up { color: #4caf50; }
.detail-change.down { color: #f44336; }

.icon-btn {
  background: transparent; border: 1px solid #2a2a3e;
  color: #555; border-radius: 6px;
  width: 32px; height: 32px; cursor: pointer; font-size: 14px;
  transition: all 0.2s; flex-shrink: 0;
}
.icon-btn:hover { background: #1e1e2e; color: #fff; }

.detail-content { display: flex; flex-direction: column; gap: 20px; }

.chart-indicator-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.chart-col { flex: 1; min-width: 0; }
.indicator-col { width: 280px; flex-shrink: 0; }

/* 圖表樣式選擇 */
.drawer-section { margin-bottom: 20px; }
.drawer-section-label {
  font-size: 11px; color: #555; text-transform: uppercase;
  letter-spacing: 1px; margin-bottom: 10px;
}
.chart-type-row { display: flex; gap: 6px; }
.chart-type-btn {
  flex: 1;
  background: #0a0a14; border: 1px solid #2a2a3e; color: #666;
  border-radius: 8px; padding: 8px 0; font-size: 13px;
  cursor: pointer; transition: all 0.15s;
}
.chart-type-btn:hover { background: #1e1e2e; color: #aaa; }
.chart-type-btn.active { background: #4361ee; border-color: #4361ee; color: #fff; }

.remove-btn {
  background: transparent; border: none;
  color: #555; cursor: pointer; font-size: 14px; padding: 2px 6px;
  border-radius: 4px; transition: all 0.15s;
}
.remove-btn:hover { color: #f44336; background: rgba(244,67,54,0.1); }
</style>
