<template>
  <div class="login-container">
    <form @submit.prevent="handleSubmit" class="login-form">
      <div class="login-header">
        <h1>Welcome Back</h1>
        <p>Sign in to your shipment management account</p>
      </div>
      <div class="form-group">
        <label for="username">Username</label>
        <input
          type="text"
          id="username"
          v-model="credentials.username"
          required
          autocomplete="username"
          placeholder="Enter your username"
          class="form-control"
        />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          v-model="credentials.password"
          required
          autocomplete="current-password"
          placeholder="Enter your password"
          class="form-control"
        />
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" :disabled="loading" class="btn-primary">
        {{ loading ? 'Signing in...' : 'Sign In' }}
      </button>
      <div class="login-footer">
        <p>Test credentials: <strong>testuser</strong> / <strong>password123</strong></p>
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
    
    router.push('/shipments')
  } catch (err) {
    console.error('Login error details:', err)
    error.value = 'Invalid username or password'
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
}

.login-form {
  background: white;
  padding: 3rem;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 450px;
  animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h1 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: 700;
}

.login-header p {
  color: #6c757d;
  margin: 0;
  font-size: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.95rem;
}

.form-control {
  width: 100%;
  padding: 0.875rem;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.btn-primary {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error {
  color: #dc3545;
  margin-bottom: 1rem;
  text-align: center;
  padding: 0.75rem;
  background-color: #f8d7da;
  border-radius: 8px;
  border: 1px solid #f5c6cb;
}

.login-footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.login-footer p {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 0;
}

.login-footer strong {
  color: #495057;
}
</style>