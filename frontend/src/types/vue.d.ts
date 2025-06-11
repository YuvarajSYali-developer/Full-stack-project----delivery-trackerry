import { DefineComponent } from 'vue'

declare module 'vue' {
  export interface GlobalComponents {
    RouterLink: typeof import('vue-router')['RouterLink']
    RouterView: typeof import('vue-router')['RouterView']
  }
}

declare global {
  interface Window {
    $toast?: {
      success: (message: string, title?: string) => void
      error: (message: string, title?: string) => void
      warning: (message: string, title?: string) => void
      info: (message: string, title?: string) => void
    }
  }
}

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $router: import('vue-router').Router
    $route: import('vue-router').RouteLocationNormalizedLoaded
  }
} 