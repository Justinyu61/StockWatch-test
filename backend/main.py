from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import stocks, ws
from app.scheduler.jobs import create_scheduler, broadcast_fn
import app.scheduler.jobs as jobs

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動排程，注入 WebSocket 廣播函式
    jobs.broadcast_fn = ws.manager.broadcast
    scheduler = create_scheduler()
    scheduler.start()
    print("✅ StockWatch 排程已啟動，每 60 秒更新一次")
    yield
    scheduler.shutdown()

app = FastAPI(title="StockWatch API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(ws.router)

@app.get("/health")
def health():
    return {"status": "ok"}
