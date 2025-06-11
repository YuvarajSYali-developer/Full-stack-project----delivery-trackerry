import { authService } from './api';
import type { LoginCredentials, User } from '../types';

export const login = async (username: string, password: string) => {
  try {
    const credentials: LoginCredentials = { username, password };
    const response = await authService.login(credentials);
    localStorage.setItem('token', response.access_token);
    return response;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem('token');
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

export const getCurrentUser = async (): Promise<User | null> => {
  try {
    if (!isAuthenticated()) {
      return null;
    }
    return await authService.getCurrentUser();
  } catch (error) {
    console.error('Failed to get current user:', error);
    return null;
  }
}; 