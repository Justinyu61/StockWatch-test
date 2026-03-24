import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const WS_BASE = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

export interface StockQuote {
  symbol: string
  name?: string
  price: number
  open: number
  high: number
  low: number
  volume: number
  prev_close: number
  change_pct: number
  recorded_at: string
}

export interface Indicators {
  symbol: string
  ma5: number
  ma20: number
  ma60: number
  rsi14: number
  macd: { macd: number; signal: number; hist: number }
}

export const useStockStore = defineStore('stock', () => {
  const watchlist = ref<{ symbol: string; name: string; market: string }[]>([])
  const quotes = ref<Record<string, StockQuote>>({})
  const indicators = ref<Record<string, Indicators>>({})
  const wsConnected = ref(false)
  const indicatorLoading = ref<Record<string, boolean>>({})
  const indicatorError = ref<Record<string, string>>({})
  const chartType = ref<'area' | 'line' | 'candle'>('area')

  async function fetchWatchlist() {
    const { data } = await axios.get(`${API}/api/watchlist`)
    watchlist.value = data
  }

  async function fetchIndicators(symbol: string) {
    indicatorLoading.value[symbol] = true
    indicatorError.value[symbol] = ''
    try {
      const { data } = await axios.get(`${API}/api/indicators/${symbol}`, { timeout: 15000 })
      if (data?.error) {
        indicatorError.value[symbol] = data.error
      } else {
        indicators.value[symbol] = data
      }
    } catch (e: any) {
      indicatorError.value[symbol] = '無法連線後端，請確認後端是否啟動'
    } finally {
      indicatorLoading.value[symbol] = false
    }
  }

  function connectWebSocket() {
    const ws = new WebSocket(`${WS_BASE}/ws/stocks`)
    ws.onopen = () => { wsConnected.value = true }
    ws.onclose = () => {
      wsConnected.value = false
      setTimeout(connectWebSocket, 3000) // 自動重連
    }
    ws.onmessage = (e) => {
      const data: StockQuote = JSON.parse(e.data)
      quotes.value[data.symbol] = data
    }
  }

  return { watchlist, quotes, indicators, indicatorLoading, indicatorError, wsConnected, chartType, fetchWatchlist, fetchIndicators, connectWebSocket }
})
