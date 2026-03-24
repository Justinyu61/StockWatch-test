import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional

# 簡單記憶體快取，TTL = 5 分鐘
_history_cache: dict = {}
_CACHE_TTL = timedelta(minutes=5)

def get_history_cached(symbol: str, period: str = "3mo"):
    key = f"{symbol}:{period}"
    now = datetime.utcnow()
    if key in _history_cache:
        df, ts = _history_cache[key]
        if now - ts < _CACHE_TTL:
            return df
    df = _fetch_history(symbol, period)
    if df is not None:
        _history_cache[key] = (df, now)
    return df

def _fetch_history(symbol: str, period: str):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return df if not df.empty else None
    except Exception as e:
        print(f"[fetcher] {symbol} 歷史資料失敗: {e}")
        return None

def get_quote(symbol: str) -> Optional[dict]:
    """抓單支股票報價，用 history() 取最新交易日資料"""
    try:
        ticker = yf.Ticker(symbol)
        # 抓最近 5 天確保有資料（週末/假日也能取到最後交易日）
        df = ticker.history(period="5d")
        if df is None or df.empty:
            return None

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else latest
        price = float(latest["Close"])
        prev_close = float(prev["Close"])
        change_pct = (price - prev_close) / prev_close * 100

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "open": round(float(latest["Open"]), 2),
            "high": round(float(latest["High"]), 2),
            "low": round(float(latest["Low"]), 2),
            "volume": int(latest["Volume"]),
            "prev_close": round(prev_close, 2),
            "change_pct": round(change_pct, 2),
            "recorded_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        print(f"[fetcher] {symbol} 抓取失敗: {e}")
        return None

def get_history(symbol: str, period: str = "3mo") -> Optional[object]:
    """抓歷史資料（有快取，5 分鐘 TTL）"""
    return get_history_cached(symbol, period)
