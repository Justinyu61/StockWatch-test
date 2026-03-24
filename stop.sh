#!/bin/bash
# StockWatch 停止腳本

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
GREEN='\033[0;32m'
NC='\033[0m'

echo "🛑 停止 StockWatch..."

# 用 PID 檔案停止
for SERVICE in backend frontend; do
  PID_FILE="$ROOT_DIR/.$SERVICE.pid"
  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    kill -9 "$PID" 2>/dev/null
    rm "$PID_FILE"
  fi
done

# 確保 port 乾淨
for PORT in 8000 3000; do
  lsof -ti:$PORT | xargs kill -9 2>/dev/null
done

echo -e "${GREEN}✅ 已停止所有服務${NC}"
