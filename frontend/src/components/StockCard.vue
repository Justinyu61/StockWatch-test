<template>
  <div class="card" :class="{ active, up: isUp, down: isDown }" @click="$emit('click')">
    <div class="top">
      <div>
        <div class="name">{{ name || symbol }}</div>
        <div class="symbol">{{ symbol }}</div>
      </div>
      <div class="change-badge" :class="isUp ? 'up' : isDown ? 'down' : ''">
        <span v-if="quote">{{ isUp ? '▲' : '▼' }} {{ Math.abs(quote.change_pct).toFixed(2) }}%</span>
        <span v-else class="skeleton">- -</span>
      </div>
    </div>

    <div v-if="quote" class="price-row">
      <span class="price">{{ quote.price.toFixed(2) }}</span>
    </div>
    <div v-else class="price-row skeleton-price">---</div>

    <div v-if="quote" class="sub-row">
      <span class="sub-item"><span class="sub-label">開</span>{{ quote.open.toFixed(2) }}</span>
      <span class="sub-item"><span class="sub-label">高</span><span class="text-up">{{ quote.high.toFixed(2) }}</span></span>
      <span class="sub-item"><span class="sub-label">低</span><span class="text-down">{{ quote.low.toFixed(2) }}</span></span>
    </div>

    <div v-if="quote" class="vol-row">
      <span class="sub-label">量</span> {{ formatVolume(quote.volume) }}
      <span class="prev">昨收 {{ quote.prev_close.toFixed(2) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { StockQuote } from '@/stores/stock'

const props = defineProps<{
  symbol: string
  name?: string
  quote?: StockQuote
  active?: boolean
}>()
defineEmits(['click'])

const isUp = computed(() => (props.quote?.change_pct ?? 0) >= 0)
const isDown = computed(() => (props.quote?.change_pct ?? 0) < 0)

function formatVolume(v: number) {
  if (v >= 1_000_000) return (v / 1_000_000).toFixed(2) + 'M'
  if (v >= 1_000) return (v / 1_000).toFixed(0) + 'K'
  return String(v)
}
</script>

<style scoped>
.card {
  background: #12121e;
  border: 1px solid #1e1e2e;
  border-radius: 14px;
  padding: 18px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}
.card:hover { background: #16162a; border-color: #2a2a3e; transform: translateY(-1px); }
.card.active { border-color: #4361ee; background: #14142a; }

.top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }

.name { font-size: 16px; font-weight: 600; color: #fff; margin-bottom: 2px; }
.symbol { font-size: 12px; color: #555; }

.change-badge {
  font-size: 13px; font-weight: 600;
  padding: 4px 10px; border-radius: 20px;
  background: #1e1e2e; color: #888;
}
.change-badge.up { background: rgba(76, 175, 80, 0.15); color: #4caf50; }
.change-badge.down { background: rgba(244, 67, 54, 0.15); color: #f44336; }

.price-row { margin-bottom: 10px; }
.price { font-size: 28px; font-weight: 700; color: #fff; letter-spacing: -0.5px; }
.skeleton-price { font-size: 28px; color: #333; }

.sub-row {
  display: flex; gap: 12px;
  margin-bottom: 8px;
  font-size: 13px; color: #aaa;
}
.sub-item { display: flex; gap: 4px; }
.sub-label { color: #555; font-size: 11px; }
.text-up { color: #4caf50; }
.text-down { color: #f44336; }

.vol-row {
  font-size: 12px; color: #555;
  display: flex; gap: 6px; align-items: center;
}
.prev { margin-left: auto; }

.skeleton { color: #333; }
</style>
