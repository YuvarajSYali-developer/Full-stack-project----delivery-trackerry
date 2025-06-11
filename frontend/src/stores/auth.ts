import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '../types';
import { authService } from '../services/api';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem('token'));
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!token.value);

  async function login(username: string, password: string) {
    try {
      loading.value = true;
      error.value = null;
      const response = await authService.login({ username, password });
      token.value = response.access_token;
      localStorage.setItem('token', response.access_token);
      await fetchUser();
    } catch (err) {
      error.value = 'Invalid username or password';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchUser() {
    try {
      const userData = await authService.getCurrentUser();
      user.value = userData;
    } catch (err) {
      console.error('Error fetching user:', err);
      logout();
    }
  }

  function logout() {
    user.value = null;
    token.value = null;
    localStorage.removeItem('token');
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    fetchUser
  };
}); 