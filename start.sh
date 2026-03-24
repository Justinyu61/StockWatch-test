#!/bin/bash
# StockWatch 一鍵啟動腳本

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "🚀 StockWatch 啟動中..."
echo "================================"

# ── 1. 清除舊 Port ──────────────────
# 只清除由本腳本啟動的程序（避免殺掉 Go API 等其他服務）
for PORT in 8000 3000; do
  PID=$(lsof -ti:$PORT 2>/dev/null)
  if [ -n "$PID" ]; then
    PROC=$(ps -p $PID -o comm= 2>/dev/null)
    # 只殺 python/node/uvicorn，不動其他程序（如 Go API、Cursor）
    if echo "$PROC" | grep -qiE "python|node|uvicorn"; then
      echo -e "${YELLOW}⚠️  Port $PORT 被 $PROC 佔用，清除中...${NC}"
      kill -9 $PID 2>/dev/null
      sleep 1
    else
      echo -e "${YELLOW}⚠️  Port $PORT 已被 $PROC 佔用，自動改用下一個可用 port（strictPort=false）${NC}"
      # 不退出，讓 vite strictPort:false 自動換 port
    fi
  fi
done

# ── 2. 確認 Python ──────────────────
if command -v python3 &>/dev/null; then
  PYTHON=python3
elif command -v python &>/dev/null; then
  PYTHON=python
else
  echo -e "${RED}❌ 找不到 Python，請先安裝 Python 3${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Python：$($PYTHON --version)${NC}"

# ── 3. 確認 Node / npm ─────────────
if ! command -v npm &>/dev/null; then
  echo -e "${RED}❌ 找不到 npm，請先安裝 Node.js${NC}"
  exit 1
fi
echo -e "${GREEN}✅ Node：$(node --version) / npm：$(npm --version)${NC}"

# ── 4. 後端 venv ───────────────────
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}📦 建立 Python 虛擬環境...${NC}"
  $PYTHON -m venv venv
fi
source venv/bin/activate
VENV_PYTHON="$BACKEND_DIR/venv/bin/python3"

# ── 5. 安裝後端套件（如有新增）────
echo -e "${YELLOW}📦 檢查後端依賴...${NC}"
$VENV_PYTHON -m pip install -q --upgrade pip
$VENV_PYTHON -m pip install -q -r requirements.txt
echo -e "${GREEN}✅ 後端依賴完成${NC}"

# ── 6. 啟動後端（背景）─────────────
echo -e "${YELLOW}🔧 啟動後端 (port 8000)...${NC}"
$VENV_PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$ROOT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$ROOT_DIR/.backend.pid"

# 等後端就緒
for i in {1..15}; do
  sleep 1
  if curl -s http://localhost:8000/health &>/dev/null; then
    echo -e "${GREEN}✅ 後端啟動成功 → http://localhost:8000${NC}"
    break
  fi
  if [ $i -eq 15 ]; then
    echo -e "${RED}❌ 後端啟動失敗，查看 backend.log${NC}"
    exit 1
  fi
done

# ── 7. 前端依賴（如未安裝）────────
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}📦 安裝前端依賴...${NC}"
  npm install --cache /tmp/npm-cache -q
fi

# ── 8. 啟動前端（背景）─────────────
echo -e "${YELLOW}🎨 啟動前端 (port 3000)...${NC}"
npm run dev > "$ROOT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$ROOT_DIR/.frontend.pid"

sleep 3
echo -e "${GREEN}✅ 前端啟動成功 → http://localhost:3000${NC}"

echo ""
echo "================================"
echo -e "${GREEN}🎉 StockWatch 已啟動！${NC}"
echo ""
echo "  📊 前端 Dashboard → http://localhost:3000"
echo "  🔧 後端 API Docs  → http://localhost:8000/docs"
echo ""
echo "  停止服務請執行：bash stop.sh"
echo "  查看後端 log：tail -f backend.log"
echo "================================"

# 開瀏覽器（macOS）
sleep 1
open http://localhost:3000 2>/dev/null || true
