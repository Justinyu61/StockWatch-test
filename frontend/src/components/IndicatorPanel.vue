<template>
  <div class="panel" :class="{ 'panel-aside': props.aside }">
    <div v-if="store.indicatorLoading[props.symbol]" class="loading">
      <span class="spin">⟳</span> 計算中...
    </div>
    <div v-else-if="store.indicatorError[props.symbol]" class="error-state">
      <span>⚠️ {{ store.indicatorError[props.symbol] }}</span>
      <button class="retry-btn" @click="store.fetchIndicators(props.symbol)">重試</button>
    </div>
    <div v-else-if="!ind" class="loading">
      <span>⏳ 等待資料...</span>
    </div>

    <!-- Aside 精簡版 -->
    <div v-else-if="props.aside" class="aside-indicators">
      <div class="aside-section-title">均線</div>
      <div class="aside-row">
        <div class="aside-item">
          <span class="aside-label">MA5</span>
          <span class="aside-val">{{ ind.ma5 ?? '-' }}</span>
        </div>
        <div class="aside-item">
          <span class="aside-label">MA20</span>
          <span class="aside-val">{{ ind.ma20 ?? '-' }}</span>
        </div>
        <div class="aside-item">
          <span class="aside-label">MA60</span>
          <span class="aside-val">{{ ind.ma60 ?? '-' }}</span>
        </div>
      </div>
      <div class="aside-signal-badge" :class="maStatus.class">
        <span class="aside-signal-label">{{ maStatus.label }}</span>
        <span class="aside-signal-hint">{{ maStatus.hint }}</span>
      </div>

      <div class="aside-divider"></div>

      <div class="aside-section-title">RSI (14)</div>
      <div class="aside-rsi-row">
        <div class="aside-rsi-bar">
          <div class="rsi-zone danger-zone">超買</div>
          <div class="rsi-zone safe-zone">正常</div>
          <div class="rsi-zone success-zone">超賣</div>
          <div class="rsi-pointer" :style="{ bottom: rsiPointerPct + '%' }"></div>
        </div>
        <div class="aside-rsi-info">
          <span class="aside-rsi-val" :class="rsiStatus.class">{{ ind.rsi14 }}</span>
          <span class="aside-rsi-hint">{{ rsiStatus.hint }}</span>
        </div>
      </div>

      <div class="aside-divider"></div>

      <div class="aside-section-title">MACD</div>
      <div class="aside-row">
        <div class="aside-item">
          <span class="aside-label">MACD</span>
          <span class="aside-val">{{ ind.macd.macd?.toFixed(2) ?? '-' }}</span>
        </div>
        <div class="aside-item">
          <span class="aside-label">Signal</span>
          <span class="aside-val">{{ ind.macd.signal?.toFixed(2) ?? '-' }}</span>
        </div>
      </div>
      <div class="aside-signal-badge" :class="macdStatus.class">
        <span class="aside-signal-hint">Hist {{ ind.macd.hist?.toFixed(3) ?? '-' }} · {{ macdStatus.hint }}</span>
      </div>
    </div>

    <!-- 一般完整版 -->
    <div v-else class="indicators">
      <!-- MA 均線 -->
      <div class="section">
        <div class="section-title">均線（Moving Average）</div>
        <div class="row">
          <div class="badge neutral">
            <span class="label">MA 5</span>
            <span class="val">{{ ind.ma5 ?? '-' }}</span>
            <span class="hint">5日均</span>
          </div>
          <div class="badge neutral">
            <span class="label">MA 20</span>
            <span class="val">{{ ind.ma20 ?? '-' }}</span>
            <span class="hint">月均</span>
          </div>
          <div class="badge neutral">
            <span class="label">MA 60</span>
            <span class="val">{{ ind.ma60 ?? '資料不足' }}</span>
            <span class="hint">季均</span>
          </div>
          <div class="badge" :class="maStatus.class">
            <span class="label">MA 訊號</span>
            <span class="val signal-text">{{ maStatus.label }}</span>
            <span class="hint">{{ maStatus.hint }}</span>
          </div>
        </div>
      </div>

      <!-- RSI -->
      <div class="section">
        <div class="section-title">RSI 相對強弱指標</div>
        <div class="row">
          <div class="badge" :class="rsiStatus.class" style="min-width:160px">
            <span class="label">RSI (14)</span>
            <span class="val">{{ ind.rsi14 }}</span>
            <span class="hint">{{ rsiStatus.hint }}</span>
          </div>
          <div class="rsi-bar-wrap">
            <div class="rsi-bar">
              <div class="rsi-zone danger-zone">超買 &gt;70</div>
              <div class="rsi-zone safe-zone">正常</div>
              <div class="rsi-zone success-zone">超賣 &lt;30</div>
              <div class="rsi-pointer" :style="{ bottom: rsiPointerPct + '%' }"></div>
            </div>
            <div class="rsi-explain">
              <span>📈 &lt;30 超賣 → 考慮進場</span>
              <span>📉 &gt;70 超買 → 考慮退場</span>
            </div>
          </div>
        </div>
      </div>

      <!-- MACD -->
      <div class="section">
        <div class="section-title">MACD 指標</div>
        <div class="row">
          <div class="badge neutral">
            <span class="label">MACD</span>
            <span class="val">{{ ind.macd.macd?.toFixed(3) ?? '-' }}</span>
          </div>
          <div class="badge neutral">
            <span class="label">Signal</span>
            <span class="val">{{ ind.macd.signal?.toFixed(3) ?? '-' }}</span>
          </div>
          <div class="badge" :class="macdStatus.class">
            <span class="label">柱狀 Hist</span>
            <span class="val">{{ ind.macd.hist?.toFixed(3) ?? '-' }}</span>
            <span class="hint">{{ macdStatus.hint }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useStockStore } from '@/stores/stock'

const props = defineProps<{ symbol: string; aside?: boolean }>()
const store = useStockStore()

const ind = computed(() => store.indicators[props.symbol])

const rsiPointerPct = computed(() => {
  if (!ind.value) return 50
  return Math.min(Math.max(ind.value.rsi14, 0), 100)
})

const rsiStatus = computed(() => {
  if (!ind.value) return { class: 'neutral', hint: '' }
  if (ind.value.rsi14 >= 70) return { class: 'danger', hint: '⚠️ 超買，考慮退場' }
  if (ind.value.rsi14 <= 30) return { class: 'success', hint: '✅ 超賣，考慮進場' }
  return { class: 'neutral', hint: '正常區間，持續觀察' }
})

const maStatus = computed(() => {
  if (!ind.value) return { class: 'neutral', label: '-', hint: '' }
  if (ind.value.ma5 > ind.value.ma20) return { class: 'success', label: '多頭排列', hint: '短均 > 長均，趨勢向上' }
  if (ind.value.ma5 < ind.value.ma20) return { class: 'danger', label: '空頭排列', hint: '短均 < 長均，趨勢向下' }
  return { class: 'neutral', label: '持平', hint: '均線糾結中' }
})

const macdStatus = computed(() => {
  if (!ind.value) return { class: 'neutral', hint: '' }
  if (ind.value.macd.hist > 0) return { class: 'success', hint: '📈 多頭動能增強' }
  return { class: 'danger', hint: '📉 空頭動能增強' }
})

onMounted(() => store.fetchIndicators(props.symbol))
</script>

<style scoped>
.panel { }
.loading { color: #555; padding: 20px 0; font-size: 13px; }
.error-state {
  display: flex; align-items: center; gap: 12px;
  padding: 16px; background: rgba(244,67,54,0.08);
  border: 1px solid rgba(244,67,54,0.2); border-radius: 8px;
  color: #f44336; font-size: 13px;
}
.retry-btn {
  background: #1e1e2e; border: 1px solid #2a2a3e;
  color: #aaa; border-radius: 6px; padding: 4px 12px;
  cursor: pointer; font-size: 12px; white-space: nowrap;
}
.retry-btn:hover { background: #2a2a3e; color: #fff; }
@keyframes spin { to { transform: rotate(360deg); } }
.spin { display: inline-block; animation: spin 1s linear infinite; }

.section { margin-bottom: 24px; }
.section-title {
  font-size: 12px; color: #555; text-transform: uppercase;
  letter-spacing: 1px; margin-bottom: 12px;
  padding-bottom: 6px; border-bottom: 1px solid #1e1e2e;
}

.row { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-start; }

.badge {
  background: #0a0a14; border-radius: 10px; padding: 12px 16px;
  display: flex; flex-direction: column; gap: 4px; min-width: 100px;
  border: 1px solid #1e1e2e;
}
.badge.success { border-color: #4caf50; background: rgba(76,175,80,0.05); }
.badge.danger  { border-color: #f44336; background: rgba(244,67,54,0.05); }
.badge.neutral { border-color: #1e1e2e; }

.label { font-size: 11px; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }
.val { font-size: 22px; font-weight: 700; color: #fff; }
.signal-text { font-size: 16px; }
.hint { font-size: 12px; color: #888; }

.badge.success .val { color: #4caf50; }
.badge.danger  .val { color: #f44336; }

/* RSI Bar */
.rsi-bar-wrap { display: flex; gap: 12px; align-items: center; }
.rsi-bar {
  width: 18px; height: 120px; border-radius: 9px;
  background: #1e1e2e; position: relative; overflow: hidden;
  display: flex; flex-direction: column;
}
.rsi-zone { flex: 1; display: flex; align-items: center; justify-content: center; font-size: 9px; }
.danger-zone  { background: rgba(244,67,54,0.2);  color: #f44336; }
.safe-zone    { background: rgba(255,255,255,0.03); color: #555; }
.success-zone { background: rgba(76,175,80,0.2);  color: #4caf50; }
.rsi-pointer {
  position: absolute; left: 0; right: 0; height: 3px;
  background: #fff; border-radius: 2px;
  transition: bottom 0.5s ease;
}
.rsi-explain {
  display: flex; flex-direction: column; gap: 6px;
  font-size: 12px; color: #666;
}

/* ─── Aside 精簡版 ─── */
.panel-aside { }

.aside-indicators { display: flex; flex-direction: column; gap: 10px; }

.aside-section-title {
  font-size: 10px; color: #555; text-transform: uppercase;
  letter-spacing: 1px; margin-bottom: 2px;
}

.aside-row { display: flex; gap: 6px; }
.aside-item {
  flex: 1; background: #0a0a14; border: 1px solid #1e1e2e;
  border-radius: 8px; padding: 8px 10px;
  display: flex; flex-direction: column; gap: 2px;
}
.aside-label { font-size: 10px; color: #555; text-transform: uppercase; }
.aside-val { font-size: 14px; font-weight: 700; color: #fff; }

.aside-signal-badge {
  border-radius: 8px; padding: 8px 12px;
  border: 1px solid #1e1e2e; background: #0a0a14;
  display: flex; flex-direction: column; gap: 2px;
}
.aside-signal-badge.success { border-color: #4caf50; background: rgba(76,175,80,0.07); }
.aside-signal-badge.danger  { border-color: #f44336; background: rgba(244,67,54,0.07); }
.aside-signal-badge.neutral { border-color: #1e1e2e; }
.aside-signal-label { font-size: 15px; font-weight: 700; color: #fff; }
.aside-signal-badge.success .aside-signal-label { color: #4caf50; }
.aside-signal-badge.danger  .aside-signal-label { color: #f44336; }
.aside-signal-hint  { font-size: 11px; color: #888; }

.aside-divider { height: 1px; background: #1e1e2e; }

.aside-rsi-row { display: flex; gap: 12px; align-items: center; }
.aside-rsi-bar {
  width: 14px; height: 90px; border-radius: 7px;
  background: #1e1e2e; position: relative; overflow: hidden;
  display: flex; flex-direction: column; flex-shrink: 0;
}
.aside-rsi-info { display: flex; flex-direction: column; gap: 4px; }
.aside-rsi-val {
  font-size: 22px; font-weight: 700; color: #fff;
}
.aside-rsi-val.success { color: #4caf50; }
.aside-rsi-val.danger  { color: #f44336; }
.aside-rsi-hint { font-size: 11px; color: #888; }
</style>
