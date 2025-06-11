import axios from 'axios';
import type {
  User,
  LoginCredentials,
  UserCreate,
  Shipment,
  ShipmentCreate,
  ShipmentUpdate,
  DashboardAnalytics
} from '../types';

const API_URL = 'http://localhost:8001';

console.log('API URL:', API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  timeout: 5000, // 5 second timeout
});

// Add request interceptor to add auth token
api.interceptors.request.use((config) => {
  console.log('Making request to:', config.url);
  console.log('Request config:', config);
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    console.log('Response received:', response);
    return response;
  },
  (error) => {
    console.error('API Error:', {
      message: error.message,
      code: error.code,
      config: error.config,
      response: error.response
    });
    if (error.code === 'ERR_NETWORK') {
      console.error('Network error - Please check if the server is running at', API_URL);
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async login(credentials: LoginCredentials): Promise<{ access_token: string; token_type: string }> {
    try {
      console.log('Login attempt with credentials:', credentials);

      // Create URL encoded form data
      const params = new URLSearchParams();
      params.append('username', credentials.username);
      params.append('password', credentials.password);

      console.log('Sending login request with params:', params.toString());
      const response = await api.post('/token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      console.log('Login response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      if (axios.isAxiosError(error)) {
        console.error('Error details:', {
          status: error.response?.status,
          data: error.response?.data,
          headers: error.response?.headers
        });
      }
      throw error;
    }
  },

  async register(userData: Omit<User, 'id'>): Promise<User> {
    const response = await api.post('/users/', userData);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/users/me');
    return response.data;
  }
};

export const shipmentService = {
  async getShipments(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    priority?: string;
    search?: string;
    customer_id?: number;
  }): Promise<Shipment[]> {
    const response = await api.get('/shipments/', { params });
    return response.data;
  },

  async getAllShipments(): Promise<Shipment[]> {
    return this.getShipments();
  },

  async getShipment(id: number): Promise<Shipment> {
    const response = await api.get(`/shipments/${id}`);
    return response.data;
  },

  async trackShipment(trackingNumber: string): Promise<Shipment> {
    const response = await api.get(`/shipments/track/${trackingNumber}`);
    return response.data;
  },

  async createShipment(shipment: ShipmentCreate): Promise<Shipment> {
    const response = await api.post('/shipments/', shipment);
    return response.data;
  },

  async updateShipment(id: number, shipment: ShipmentUpdate): Promise<Shipment> {
    const response = await api.patch(`/shipments/${id}`, shipment);
    return response.data;
  },

  async deleteShipment(id: number): Promise<void> {
    await api.delete(`/shipments/${id}`);
  },

  async getTrackingHistory(shipmentId: number): Promise<TrackingHistory[]> {
    const response = await api.get(`/shipments/${shipmentId}/tracking`);
    return response.data;
  },

  async addTrackingUpdate(shipmentId: number, tracking: TrackingHistoryCreate): Promise<TrackingHistory> {
    const response = await api.post(`/shipments/${shipmentId}/tracking`, tracking);
    return response.data;
  },

  async getDashboardAnalytics(): Promise<DashboardAnalytics> {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  }
};

export const notificationService = {
  async getNotifications(params?: {
    skip?: number;
    limit?: number;
    unread_only?: boolean;
  }): Promise<Notification[]> {
    const response = await api.get('/notifications/', { params });
    return response.data;
  },

  async createNotification(notification: NotificationCreate): Promise<Notification> {
    const response = await api.post('/notifications/', notification);
    return response.data;
  },

  async markAsRead(notificationId: number): Promise<void> {
    await api.patch(`/notifications/${notificationId}/read`);
  }
};

export const adminService = {
  async getAllUsers(params?: {
    skip?: number;
    limit?: number;
    role?: string;
  }): Promise<User[]> {
    const response = await api.get('/admin/users/', { params });
    return response.data;
  },

  async updateUserRole(userId: number, newRole: string): Promise<void> {
    await api.patch(`/admin/users/${userId}/role`, { new_role: newRole });
  },

  async toggleUserStatus(userId: number): Promise<void> {
    await api.patch(`/admin/users/${userId}/status`);
  }
};

export default api; 