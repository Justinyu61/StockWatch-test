import httpx
from app.core.config import settings
from app.services.fetcher import get_quote, get_history
from app.services.indicators import calc_rsi, check_ma_cross

async def send_line_message(text: str):
    """發送 LINE 通知"""
    if not settings.line_channel_access_token or not settings.line_user_id:
        print(f"[alert] LINE 未設定，訊息：{text}")
        return
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.line.me/v2/bot/message/push",
            headers={"Authorization": f"Bearer {settings.line_channel_access_token}"},
            json={
                "to": settings.line_user_id,
                "messages": [{"type": "text", "text": text}]
            }
        )

async def evaluate_alert(alert: dict, quote: dict, df):
    """根據提醒規則判斷是否觸發"""
    symbol = alert["symbol"]
    alert_type = alert["alert_type"]
    condition = alert["condition"]
    price = quote["price"]

    triggered = False
    message = ""

    if alert_type == "price_above":
        target = condition["price"]
        if price >= target:
            triggered = True
            message = f"📈 {symbol} 突破目標價 {target}\n現價：{price}"

    elif alert_type == "price_below":
        target = condition["price"]
        if price <= target:
            triggered = True
            message = f"📉 {symbol} 跌破 {target}\n現價：{price}"

    elif alert_type == "rsi_overbought":
        rsi = calc_rsi(df)
        if rsi >= condition.get("threshold", 70):
            triggered = True
            message = f"⚠️ {symbol} RSI 超買（{rsi}），考慮退場"

    elif alert_type == "rsi_oversold":
        rsi = calc_rsi(df)
        if rsi <= condition.get("threshold", 30):
            triggered = True
            message = f"✅ {symbol} RSI 超賣（{rsi}），考慮進場"

    elif alert_type == "ma_cross":
        short = condition.get("short", 5)
        long = condition.get("long", 20)
        cross = check_ma_cross(df, short, long)
        if cross == "golden":
            triggered = True
            message = f"🟢 {symbol} 均線黃金交叉（MA{short} 穿越 MA{long}），考慮進場"
        elif cross == "death":
            triggered = True
            message = f"🔴 {symbol} 均線死亡交叉（MA{short} 跌破 MA{long}），考慮退場"

    if triggered and message:
        await send_line_message(message)

    return triggered
