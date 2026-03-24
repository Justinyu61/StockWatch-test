from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.fetcher import get_quote, get_history
from app.services.indicators import calc_ma, calc_rsi, calc_macd
from app.scheduler.jobs import WATCHLIST, ALERTS, _save_watchlist
import math

def _safe(v):
    if v is None: return None
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)): return None
    return round(v, 4) if isinstance(v, float) else v

router = APIRouter(prefix="/api")

# ── Watchlist CRUD ───────────────────────────────────────────────

@router.get("/watchlist")
def get_watchlist():
    return WATCHLIST

class AddStockBody(BaseModel):
    symbol: str
    name: str = ""

@router.post("/watchlist")
def add_stock(body: AddStockBody):
    symbol = body.symbol.strip().upper()
    if any(s["symbol"] == symbol for s in WATCHLIST):
        raise HTTPException(status_code=409, detail="已存在")
    WATCHLIST.append({"symbol": symbol, "name": body.name or symbol})
    _save_watchlist()
    return {"ok": True}

@router.delete("/watchlist/{symbol}")
def remove_stock(symbol: str):
    symbol = symbol.upper()
    idx = next((i for i, s in enumerate(WATCHLIST) if s["symbol"] == symbol), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="不存在")
    WATCHLIST.pop(idx)
    _save_watchlist()
    return {"ok": True}

# ── Quotes & Indicators ──────────────────────────────────────────

@router.get("/quote/{symbol}")
def quote(symbol: str):
    return get_quote(symbol)

@router.get("/indicators/{symbol}")
def indicators(symbol: str):
    df = get_history(symbol, period="3mo")
    if df is None or df.empty:
        return {"error": "無法取得資料"}
    macd = calc_macd(df)
    return {
        "symbol": symbol,
        "ma5":   _safe(calc_ma(df, 5)),
        "ma20":  _safe(calc_ma(df, 20)),
        "ma60":  _safe(calc_ma(df, 60)),
        "rsi14": _safe(calc_rsi(df, 14)),
        "macd": {
            "macd":   _safe(macd["macd"]),
            "signal": _safe(macd["signal"]),
            "hist":   _safe(macd["hist"]),
        },
    }

@router.get("/history/{symbol}")
def history(symbol: str, period: str = "3mo"):
    df = get_history(symbol, period=period)
    if df is None or df.empty:
        return []
    df = df.reset_index()
    result = []
    for _, row in df.iterrows():
        date_val = row["Date"]
        date_str = date_val.date().isoformat() if hasattr(date_val, 'date') else str(date_val)[:10]
        result.append({
            "date":   date_str,
            "open":   round(float(row["Open"]),  2),
            "high":   round(float(row["High"]),  2),
            "low":    round(float(row["Low"]),   2),
            "close":  round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        })
    return result

@router.get("/alerts")
def get_alerts():
    return ALERTS

@router.post("/refresh")
async def refresh():
    from app.scheduler.jobs import fetch_and_check
    await fetch_and_check()
    return {"status": "refreshed"}
