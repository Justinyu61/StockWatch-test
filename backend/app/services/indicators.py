import pandas as pd
import ta

def calc_ma(df: pd.DataFrame, period: int) -> float:
    """計算移動平均線（MA）"""
    ma = df["Close"].rolling(window=period).mean()
    return round(float(ma.iloc[-1]), 2)

def calc_rsi(df: pd.DataFrame, period: int = 14) -> float:
    """計算 RSI（相對強弱指標）
    > 70 超買（考慮退場）
    < 30 超賣（考慮進場）
    """
    rsi = ta.momentum.RSIIndicator(df["Close"], window=period).rsi()
    return round(float(rsi.iloc[-1]), 2)

def calc_macd(df: pd.DataFrame) -> dict:
    """計算 MACD
    macd 線穿越 signal 線向上 → 進場訊號
    macd 線穿越 signal 線向下 → 退場訊號
    """
    macd_ind = ta.trend.MACD(df["Close"])
    return {
        "macd": round(float(macd_ind.macd().iloc[-1]), 4),
        "signal": round(float(macd_ind.macd_signal().iloc[-1]), 4),
        "hist": round(float(macd_ind.macd_diff().iloc[-1]), 4),
    }

def check_ma_cross(df: pd.DataFrame, short: int = 5, long: int = 20) -> str:
    """偵測均線交叉
    回傳 'golden'（黃金交叉，進場）/ 'death'（死亡交叉，退場）/ 'none'
    """
    ma_short = df["Close"].rolling(window=short).mean()
    ma_long = df["Close"].rolling(window=long).mean()

    prev_short = float(ma_short.iloc[-2])
    prev_long = float(ma_long.iloc[-2])
    curr_short = float(ma_short.iloc[-1])
    curr_long = float(ma_long.iloc[-1])

    if prev_short <= prev_long and curr_short > curr_long:
        return "golden"
    elif prev_short >= prev_long and curr_short < curr_long:
        return "death"
    return "none"
