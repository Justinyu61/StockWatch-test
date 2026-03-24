# StockWatch

台股 + 美股即時監控、技術指標、LINE 進退場提醒。

## 快速啟動

### 1. 後端（Python）

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填入 LINE Bot token（選填）
uvicorn main:app --reload
```

### 2. 前端（Vue 3）

```bash
cd frontend
npm install
npm run dev
```

瀏覽器開 http://localhost:5173

### 3. 用 Docker（資料庫）

```bash
docker-compose up db   # 只啟動 PostgreSQL
```

---

## 自選股設定

編輯 `backend/app/scheduler/jobs.py`：

```python
WATCHLIST = [
    {"symbol": "2330.TW", "name": "台積電"},   # 台股格式：代碼.TW
    {"symbol": "AAPL",    "name": "Apple"},    # 美股格式：代碼
]
```

## 進退場提醒設定

```python
ALERTS = [
    # 台積電跌破 800 → LINE 通知
    {"symbol": "2330.TW", "alert_type": "price_below", "condition": {"price": 800}},

    # NVDA RSI 超買 → LINE 通知
    {"symbol": "NVDA", "alert_type": "rsi_overbought", "condition": {"threshold": 70}},

    # 台積電 MA5 黃金交叉 MA20 → 進場通知
    {"symbol": "2330.TW", "alert_type": "ma_cross", "condition": {"short": 5, "long": 20}},
]
```

## 提醒類型說明

| 類型 | 說明 | 參數 |
|------|------|------|
| `price_above` | 股價突破目標價 | `{"price": 850}` |
| `price_below` | 股價跌破目標價 | `{"price": 800}` |
| `rsi_overbought` | RSI 超買（考慮退場） | `{"threshold": 70}` |
| `rsi_oversold` | RSI 超賣（考慮進場） | `{"threshold": 30}` |
| `ma_cross` | 均線交叉（黃金/死亡） | `{"short": 5, "long": 20}` |
