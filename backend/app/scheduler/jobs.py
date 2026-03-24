import json, os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from app.services.fetcher import get_quote, get_history
from app.services.alert_engine import evaluate_alert

# ── 持久化自選股（JSON 檔） ──────────────────────────────────────
_DATA_FILE = os.environ.get('WATCHLIST_PATH', '/tmp/watchlist.json')
_DEFAULT_WATCHLIST = [
    {"symbol": "2330.TW", "name": "台積電"},
    {"symbol": "2317.TW", "name": "鴻海"},
    {"symbol": "AAPL",    "name": "Apple"},
    {"symbol": "NVDA",    "name": "NVIDIA"},
]

def _load_watchlist():
    try:
        with open(_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return list(_DEFAULT_WATCHLIST)

def _save_watchlist():
    try:
        with open(_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(WATCHLIST, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

WATCHLIST = _load_watchlist()

ALERTS = [
    {"symbol": "2330.TW", "alert_type": "price_below", "condition": {"price": 800}, "is_active": True},
    {"symbol": "NVDA", "alert_type": "rsi_overbought", "condition": {"threshold": 70}, "is_active": True},
]

# 給 WebSocket broadcast 用
broadcast_fn = None

async def fetch_and_check():
    """每分鐘執行：抓報價 + 檢查提醒條件"""
    for stock in WATCHLIST:
        symbol = stock["symbol"]
        quote = get_quote(symbol)
        if not quote:
            continue
        if broadcast_fn:
            await broadcast_fn(symbol, quote)
        df = get_history(symbol, period="3mo")
        if df is None or df.empty:
            continue
        for alert in ALERTS:
            if alert["symbol"] == symbol and alert["is_active"]:
                await evaluate_alert(alert, quote, df)

def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_and_check, "interval", seconds=60, id="fetch_stocks", next_run_time=datetime.now())
    return scheduler
