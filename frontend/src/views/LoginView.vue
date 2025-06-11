<template>
  <div class="login-container">
    <!-- Background Elements -->
    <div class="bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <!-- Login Form -->
    <form @submit.prevent="handleSubmit" class="login-form glass-card animate-fade-in-scale">
      <!-- Logo Section -->
      <div class="login-logo">
        <div class="logo-icon">
          <span class="icon-gradient">📦</span>
        </div>
        <h1 class="logo-title">ShipTrack Pro</h1>
      </div>

      <!-- Header -->
      <div class="login-header">
        <h2>Welcome Back</h2>
        <p>Sign in to your shipment management account</p>
      </div>

      <!-- Form Fields -->
      <div class="form-group">
        <label for="username">
          <span class="label-icon">👤</span>
          Username
        </label>
        <div class="input-wrapper">
          <input
            type="text"
            id="username"
            v-model="credentials.username"
            required
            autocomplete="username"
            placeholder="Enter your username"
            class="form-control"
          />
          <div class="input-focus-border"></div>
        </div>
      </div>

      <div class="form-group">
        <label for="password">
          <span class="label-icon">🔒</span>
          Password
        </label>
        <div class="input-wrapper">
          <input
            type="password"
            id="password"
            v-model="credentials.password"
            required
            autocomplete="current-password"
            placeholder="Enter your password"
            class="form-control"
          />
          <div class="input-focus-border"></div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error animate-fade-in-up">
        <span class="error-icon">⚠️</span>
        {{ error }}
      </div>

      <!-- Submit Button -->
      <button type="submit" :disabled="loading" class="btn-primary">
        <span v-if="loading" class="loading-spinner"></span>
        <span class="btn-text">{{ loading ? 'Signing in...' : 'Sign In' }}</span>
        <span v-if="!loading" class="btn-arrow">→</span>
      </button>

      <!-- Footer -->
      <div class="login-footer">
        <div class="test-credentials">
          <span class="credentials-icon">🔑</span>
          <div class="credentials-text">
            <p><strong>Test Credentials:</strong></p>
            <p><code>testuser</code> / <code>password123</code></p>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/api'
import type { LoginCredentials } from '../types'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const credentials = ref<LoginCredentials>({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  try {
    console.log('Starting login process...')
    console.log('Credentials:', credentials.value)
    loading.value = true
    error.value = ''

    console.log('Calling authService.login...')
    const response = await authService.login(credentials.value)
    console.log('Login response:', response)

    localStorage.setItem('token', response.access_token)
    console.log('Token stored in localStorage')

    // Show success toast
    if (window.$toast) {
      window.$toast.success('Welcome back!', 'Login Successful')
    }

    router.push('/dashboard')
  } catch (err) {
    console.error('Login error details:', err)
    error.value = 'Invalid username or password'

    // Show error toast
    if (window.$toast) {
      window.$toast.error('Please check your credentials and try again.', 'Login Failed')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
  position: relative;
  overflow: hidden;
}

/* Background Shapes */
.bg-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* Login Form */
.login-form {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 3rem;
  border-radius: 24px;
  box-shadow:
    0 25px 50px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.2);
  width: 100%;
  max-width: 480px;
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Logo Section */
.login-logo {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
}

.icon-gradient {
  font-size: 2.5rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.logo-title {
  font-size: 1.75rem;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

/* Header */
.login-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.login-header h2 {
  color: #1e293b;
  margin: 0 0 0.5rem 0;
  font-size: 1.875rem;
  font-weight: 700;
}

.login-header p {
  color: #64748b;
  margin: 0;
  font-size: 1rem;
  font-weight: 400;
}

/* Form Groups */
.form-group {
  margin-bottom: 2rem;
}

label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  color: #1e293b;
  font-weight: 600;
  font-size: 0.95rem;
}

.label-icon {
  font-size: 1.1rem;
}

/* Input Wrapper */
.input-wrapper {
  position: relative;
}

.form-control {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  font-size: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-2px);
  box-shadow:
    0 10px 25px rgba(59, 130, 246, 0.15),
    0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control::placeholder {
  color: #94a3b8;
  font-weight: 400;
}

/* Focus Border Animation */
.input-focus-border {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  transition: all 0.3s ease;
  transform: translateX(-50%);
  border-radius: 1px;
}

.form-control:focus + .input-focus-border {
  width: 100%;
}

/* Submit Button */
.btn-primary {
  width: 100%;
  padding: 1.25rem 2rem;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow:
    0 10px 25px rgba(59, 130, 246, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  position: relative;
  overflow: hidden;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn-primary:hover:not(:disabled)::before {
  left: 100%;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow:
    0 15px 35px rgba(59, 130, 246, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}

.btn-primary:active:not(:disabled) {
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background: linear-gradient(135deg, #94a3b8, #64748b);
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 15px rgba(148, 163, 184, 0.2);
}

.btn-text {
  font-weight: 600;
}

.btn-arrow {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.btn-primary:hover:not(:disabled) .btn-arrow {
  transform: translateX(4px);
}

/* Loading Spinner */
.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error Message */
.error {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #dc2626;
  margin-bottom: 1.5rem;
  text-align: left;
  padding: 1rem 1.25rem;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(239, 68, 68, 0.2);
  backdrop-filter: blur(10px);
}

.error-icon {
  font-size: 1.2rem;
  flex-shrink: 0;
}

/* Footer */
.login-footer {
  margin-top: 2.5rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(226, 232, 240, 0.6);
}

.test-credentials {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.credentials-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.credentials-text {
  flex: 1;
}

.credentials-text p {
  color: #475569;
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.5;
}

.credentials-text p:first-child {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.credentials-text code {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
  font-size: 0.85rem;
  font-weight: 600;
}

/* Responsive Design */
@media (max-width: 640px) {
  .login-form {
    padding: 2rem 1.5rem;
    margin: 1rem;
    border-radius: 20px;
  }

  .logo-icon {
    width: 60px;
    height: 60px;
  }

  .icon-gradient {
    font-size: 2rem;
  }

  .logo-title {
    font-size: 1.5rem;
  }

  .login-header h2 {
    font-size: 1.5rem;
  }

  .test-credentials {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }

  .credentials-icon {
    margin-top: 0;
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: 0.5rem;
  }

  .login-form {
    padding: 1.5rem 1rem;
  }

  .shape {
    display: none;
  }
}
</style>