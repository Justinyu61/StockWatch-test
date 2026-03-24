const { app, BrowserWindow, shell, Menu } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const http = require('http')

let mainWindow
let backendProcess

// ─── 路徑解析 ───────────────────────────────────────────────
function getBackendDir() {
  if (app.isPackaged) {
    // 打包後：backend 放在 resources/backend
    return path.join(process.resourcesPath, 'backend')
  }
  // 開發模式：frontend/electron/main.cjs → ../../backend
  return path.join(__dirname, '..', '..', 'backend')
}

function getPythonPath(backendDir) {
  return path.join(backendDir, 'venv', 'bin', 'python3')
}

// ─── 啟動 Python 後端 ────────────────────────────────────────
function startBackend() {
  const backendDir = getBackendDir()
  const pythonPath = getPythonPath(backendDir)

  console.log('[Electron] 啟動後端:', pythonPath)
  console.log('[Electron] 後端目錄:', backendDir)

  backendProcess = spawn(
    pythonPath,
    ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'],
    {
      cwd: backendDir,
      env: { ...process.env },
    }
  )

  backendProcess.stdout.on('data', (d) => console.log('[Backend]', d.toString().trim()))
  backendProcess.stderr.on('data', (d) => console.log('[Backend]', d.toString().trim()))
  backendProcess.on('close', (code) => console.log('[Backend] 結束，代碼:', code))
}

// ─── 等待後端就緒 ─────────────────────────────────────────────
function waitForBackend(retries = 40) {
  return new Promise((resolve, reject) => {
    const check = () => {
      http
        .get('http://127.0.0.1:8000/health', () => resolve())
        .on('error', () => {
          if (retries-- > 0) setTimeout(check, 500)
          else reject(new Error('後端啟動逾時'))
        })
    }
    setTimeout(check, 800) // 給 uvicorn 一點啟動時間
  })
}

// ─── 建立視窗 ────────────────────────────────────────────────
async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 960,
    minHeight: 600,
    backgroundColor: '#0a0a10',
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    show: false,
    title: 'StockWatch',
  })

  // 先顯示載入畫面
  mainWindow.loadURL(
    'data:text/html,<html style="margin:0;background:%230a0a10;color:%23ffffff;display:flex;align-items:center;justify-content:center;height:100vh;font-family:system-ui;font-size:18px"><div>⏳ StockWatch 啟動中...</div></html>'
  )
  mainWindow.show()

  // 啟動後端
  startBackend()

  try {
    await waitForBackend()
    console.log('[Electron] 後端就緒')
  } catch (e) {
    console.warn('[Electron] 後端未能及時就緒，仍繼續載入前端')
  }

  // 載入前端
  if (process.env.ELECTRON_DEV === 'true') {
    // 開發模式：載入 Vite dev server（需先 npm run dev）
    mainWindow.loadURL('http://localhost:3000')
    mainWindow.webContents.openDevTools()
  } else {
    // 預覽 / 生產模式：載入打包後的靜態檔案
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }

  // 外部連結用瀏覽器開啟
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })
}

// ─── 隱藏選單列（保留 macOS 必要項目）────────────────────────
function setupMenu() {
  if (process.platform === 'darwin') {
    const template = [
      {
        label: app.name,
        submenu: [
          { role: 'about' },
          { type: 'separator' },
          { role: 'services' },
          { type: 'separator' },
          { role: 'hide' },
          { role: 'hideOthers' },
          { role: 'unhide' },
          { type: 'separator' },
          { role: 'quit' },
        ],
      },
      { role: 'editMenu' },
      { role: 'viewMenu' },
      { role: 'windowMenu' },
    ]
    Menu.setApplicationMenu(Menu.buildFromTemplate(template))
  } else {
    Menu.setApplicationMenu(null)
  }
}

// ─── 應用生命週期 ─────────────────────────────────────────────
app.whenReady().then(() => {
  setupMenu()
  createWindow()
})

app.on('window-all-closed', () => {
  killBackend()
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

app.on('before-quit', killBackend)

function killBackend() {
  if (backendProcess) {
    console.log('[Electron] 關閉後端...')
    backendProcess.kill('SIGTERM')
    backendProcess = null
  }
}
