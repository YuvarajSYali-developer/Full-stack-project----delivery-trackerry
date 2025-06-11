<template>
  <div class="loading-spinner-container" :class="{ 'overlay': overlay }">
    <div class="loading-spinner">
      <div class="spinner-ring">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      <p v-if="message" class="loading-message">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message?: string
  overlay?: boolean
}

withDefaults(defineProps<Props>(), {
  message: 'Loading...',
  overlay: false
})
</script>

<style scoped>
.loading-spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.loading-spinner-container.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  z-index: 9999;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner-ring {
  display: inline-block;
  position: relative;
  width: 64px;
  height: 64px;
}

.spinner-ring div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 51px;
  height: 51px;
  margin: 6px;
  border: 6px solid transparent;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spinner-ring-rotate 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.spinner-ring div:nth-child(1) { animation-delay: -0.45s; }
.spinner-ring div:nth-child(2) { animation-delay: -0.3s; }
.spinner-ring div:nth-child(3) { animation-delay: -0.15s; }

@keyframes spinner-ring-rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-message {
  color: #64748b;
  font-weight: 500;
  font-size: 0.95rem;
  margin: 0;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
