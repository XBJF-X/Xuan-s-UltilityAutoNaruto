/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface Window {
  electronAPI?: {
    selectDirectory: () => Promise<string | null>
    getAppPath: () => Promise<string>
    platform: string
  }
}