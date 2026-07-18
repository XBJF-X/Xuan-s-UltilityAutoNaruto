/**
 * Electron preload 脚本
 * 暴露安全的 API 给渲染进程
 */
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  getAppPath: () => ipcRenderer.invoke('get-app-path'),
  platform: process.platform,
})