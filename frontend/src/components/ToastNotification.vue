<template>
  <Teleport to="body">
    <div class="toast-container">
      <Transition
        v-for="toast in toasts"
        :key="toast.id"
        name="toast"
        appear
      >
        <div
          :class="[
            'toast',
            `toast-${toast.type}`,
            { 'toast-dismissible': toast.dismissible }
          ]"
        >
          <div class="toast-icon">
            {{ getIcon(toast.type) }}
          </div>
          <div class="toast-content">
            <h4 v-if="toast.title" class="toast-title">{{ toast.title }}</h4>
            <p class="toast-message">{{ toast.message }}</p>
          </div>
          <button
            v-if="toast.dismissible"
            @click="removeToast(toast.id)"
            class="toast-close"
          >
            ×
          </button>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  duration?: number
  dismissible?: boolean
}

const toasts = ref<Toast[]>([])

const getIcon = (type: string) => {
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  }
  return icons[type as keyof typeof icons] || 'ℹ️'
}

const addToast = (toast: Omit<Toast, 'id'>) => {
  const id = Date.now().toString()
  const newToast: Toast = {
    id,
    dismissible: true,
    duration: 5000,
    ...toast
  }
  
  toasts.value.push(newToast)
  
  if (newToast.duration && newToast.duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, newToast.duration)
  }
}

const removeToast = (id: string) => {
  const index = toasts.value.findIndex(toast => toast.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

// Global toast methods
const showSuccess = (message: string, title?: string) => {
  addToast({ type: 'success', message, title })
}

const showError = (message: string, title?: string) => {
  addToast({ type: 'error', message, title })
}

const showWarning = (message: string, title?: string) => {
  addToast({ type: 'warning', message, title })
}

const showInfo = (message: string, title?: string) => {
  addToast({ type: 'info', message, title })
}

// Expose methods globally
onMounted(() => {
  window.$toast = {
    success: showSuccess,
    error: showError,
    warning: showWarning,
    info: showInfo
  }
})

defineExpose({
  addToast,
  removeToast,
  showSuccess,
  showError,
  showWarning,
  showInfo
})
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 400px;
}

.toast {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 12px;
  box-shadow: 
    0 10px 25px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-width: 300px;
}

.toast-success {
  border-left: 4px solid #10b981;
}

.toast-error {
  border-left: 4px solid #ef4444;
}

.toast-warning {
  border-left: 4px solid #f59e0b;
}

.toast-info {
  border-left: 4px solid #3b82f6;
}

.toast-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.toast-message {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.toast-close:hover {
  background: rgba(148, 163, 184, 0.1);
  color: #64748b;
}

/* Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

@media (max-width: 640px) {
  .toast-container {
    left: 1rem;
    right: 1rem;
    max-width: none;
  }
  
  .toast {
    min-width: auto;
  }
}
</style>
