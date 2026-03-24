from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class WatchList(Base):
    """自選股清單"""
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)   # e.g. "2330.TW" / "AAPL"
    name = Column(String(100))                     # 顯示名稱
    market = Column(String(10))                    # "TW" / "US"
    created_at = Column(DateTime, default=datetime.utcnow)

class StockPrice(Base):
    """歷史價格快照"""
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    price = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    """進退場提醒規則"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    alert_type = Column(String(50))   # "price_above" / "price_below" / "ma_cross" / "rsi_overbought" / "rsi_oversold"
    condition = Column(JSON)          # 條件參數，如 {"price": 850} 或 {"period_short": 5, "period_long": 20}
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
