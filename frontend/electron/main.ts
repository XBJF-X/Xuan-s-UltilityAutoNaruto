/**
 * Electron 主进程
 * 负责管理 Python 后端子进程的生命周期
 */
import { app, BrowserWindow, dialog, ipcMain } from 'electron'
import { spawn, ChildProcess } from 'child_process'
import path from 'path'

let mainWindow: BrowserWindow | null = null
let pythonProcess: ChildProcess | null = null

const BACKEND_PORT = 4199
const isDev = !app.isPackaged

function getBackendPath(): string {
  if (isDev) {
    return path.join(__dirname, '..', '..', 'backend', 'main.py')
  }
  return path.join(process.resourcesPath, 'backend', 'main.py')
}

function startPythonBackend(): void {
  const backendPath = getBackendPath()
  const pythonExe = isDev ? 'python' : path.join(process.resourcesPath, 'backend', '.venv', 'Scripts', 'python.exe')

  console.log(`Starting backend: ${pythonExe} ${backendPath}`)

  pythonProcess = spawn(pythonExe, [backendPath], {
    cwd: path.dirname(backendPath),
    stdio: ['pipe', 'pipe', 'pipe'],
  })

  pythonProcess.stdout?.on('data', (data: Buffer) => {
    console.log(`[Backend] ${data.toString()}`)
  })

  pythonProcess.stderr?.on('data', (data: Buffer) => {
    console.error(`[Backend Error] ${data.toString()}`)
  })

  pythonProcess.on('close', (code: number | null) => {
    console.log(`Backend process exited with code ${code}`)
    pythonProcess = null
  })

  pythonProcess.on('error', (err) => {
    console.error('Failed to start backend:', err)
  })
}

function stopPythonBackend(): void {
  if (pythonProcess) {
    pythonProcess.kill('SIGTERM')
    setTimeout(() => {
      if (pythonProcess) {
        pythonProcess.kill('SIGKILL')
      }
    }, 5000)
  }
}

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1100,
    minHeight: 700,
    frame: false, // 无边框窗口，与原版一致
    icon: path.join(__dirname, '..', '..', 'src', 'ASDS.ico'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist', 'index.html'))
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// IPC handlers
ipcMain.handle('select-directory', async () => {
  if (!mainWindow) return null
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory'],
  })
  return result.canceled ? null : result.filePaths[0]
})

ipcMain.handle('get-app-path', () => {
  return app.getAppPath()
})

// App lifecycle
app.whenReady().then(() => {
  startPythonBackend()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  stopPythonBackend()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  stopPythonBackend()
})