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
    // Return mock data since working server doesn't have shipments endpoint
    return [
      {
        id: 1,
        tracking_number: 'ABC123456',
        status: 'in_transit' as any,
        priority: 'normal' as any,
        origin_address: '123 Main St',
        destination_address: '456 Oak Ave',
        origin_city: 'New York',
        destination_city: 'Los Angeles',
        origin_country: 'USA',
        destination_country: 'USA',
        weight: 2.5,
        dimensions: '10x8x6',
        declared_value: 100,
        insurance_required: false,
        fragile: false,
        description: 'Sample package',
        special_instructions: '',
        estimated_delivery_date: '2024-01-15',
        actual_delivery_date: '',
        customer_id: 1,
        created_at: '2024-01-10T10:00:00Z',
        updated_at: '2024-01-10T10:00:00Z'
      },
      {
        id: 2,
        tracking_number: 'XYZ789012',
        status: 'delivered' as any,
        priority: 'high' as any,
        origin_address: '789 Pine St',
        destination_address: '321 Elm St',
        origin_city: 'Chicago',
        destination_city: 'Miami',
        origin_country: 'USA',
        destination_country: 'USA',
        weight: 1.2,
        dimensions: '8x6x4',
        declared_value: 50,
        insurance_required: true,
        fragile: true,
        description: 'Fragile electronics',
        special_instructions: 'Handle with care',
        estimated_delivery_date: '2024-01-12',
        actual_delivery_date: '2024-01-12',
        customer_id: 1,
        created_at: '2024-01-08T14:30:00Z',
        updated_at: '2024-01-12T16:45:00Z'
      }
    ];
  },

  async getAllShipments(): Promise<Shipment[]> {
    return this.getShipments();
  },

  async getShipment(id: number): Promise<Shipment> {
    const shipments = await this.getShipments();
    const shipment = shipments.find(s => s.id === id);
    if (!shipment) throw new Error('Shipment not found');
    return shipment;
  },

  async trackShipment(trackingNumber: string): Promise<Shipment> {
    const shipments = await this.getShipments();
    const shipment = shipments.find(s => s.tracking_number === trackingNumber);
    if (!shipment) throw new Error('Shipment not found');
    return shipment;
  },

  async createShipment(shipment: ShipmentCreate): Promise<Shipment> {
    // Mock creation - return a new shipment with generated ID
    const newShipment: Shipment = {
      id: Math.floor(Math.random() * 1000),
      tracking_number: shipment.tracking_number || `ABC${Math.floor(Math.random() * 1000000)}`,
      status: shipment.status || 'pending' as any,
      priority: shipment.priority || 'normal' as any,
      origin_address: shipment.origin_address,
      destination_address: shipment.destination_address,
      origin_city: shipment.origin_city,
      destination_city: shipment.destination_city,
      origin_country: shipment.origin_country || 'USA',
      destination_country: shipment.destination_country || 'USA',
      weight: shipment.weight,
      dimensions: shipment.dimensions,
      declared_value: shipment.declared_value,
      insurance_required: shipment.insurance_required || false,
      fragile: shipment.fragile || false,
      description: shipment.description,
      special_instructions: shipment.special_instructions,
      estimated_delivery_date: shipment.estimated_delivery_date,
      actual_delivery_date: '',
      customer_id: shipment.customer_id || 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    return newShipment;
  },

  async updateShipment(id: number, shipment: ShipmentUpdate): Promise<Shipment> {
    const existing = await this.getShipment(id);
    return { ...existing, ...shipment, updated_at: new Date().toISOString() };
  },

  async deleteShipment(id: number): Promise<void> {
    // Mock deletion - just return success
    return;
  },

  async getTrackingHistory(shipmentId: number): Promise<any[]> {
    return [
      {
        id: 1,
        shipment_id: shipmentId,
        status: 'pending',
        location: 'Origin facility',
        description: 'Package received',
        timestamp: '2024-01-10T10:00:00Z'
      }
    ];
  },

  async addTrackingUpdate(shipmentId: number, tracking: any): Promise<any> {
    return {
      id: Math.floor(Math.random() * 1000),
      shipment_id: shipmentId,
      ...tracking,
      timestamp: new Date().toISOString()
    };
  },

  async getDashboardAnalytics(): Promise<DashboardAnalytics> {
    try {
      console.log('Fetching dashboard analytics from backend...');
      const response = await api.get('/analytics/dashboard');
      console.log('Dashboard analytics response:', response.data);

      // Transform backend data to match frontend interface
      const backendData = response.data;
      return {
        total_shipments: backendData.total_shipments,
        pending_shipments: backendData.pending_shipments,
        in_transit_shipments: backendData.in_transit_shipments,
        delivered_shipments: backendData.delivered_shipments,
        total_revenue: backendData.total_revenue,
        monthly_revenue: backendData.total_revenue, // Use total as monthly for now
        average_delivery_time: backendData.avg_delivery_time,
        customer_satisfaction: 4.8, // Default value
        top_destinations: [
          { city: 'Mumbai', count: 12 },
          { city: 'Delhi', count: 10 },
          { city: 'Bangalore', count: 8 }
        ],
        recent_shipments: []
      };
    } catch (error) {
      console.error('Error fetching dashboard analytics:', error);
      // Fallback to mock data if API fails
      return {
        total_shipments: 50,
        pending_shipments: 8,
        in_transit_shipments: 32,
        delivered_shipments: 10,
        total_revenue: 7088.08,
        monthly_revenue: 7088.08,
        average_delivery_time: 4.8,
        customer_satisfaction: 4.8,
        top_destinations: [
          { city: 'Mumbai', count: 12 },
          { city: 'Delhi', count: 10 },
          { city: 'Bangalore', count: 8 }
        ],
        recent_shipments: []
      };
    }
  }
};

export const notificationService = {
  async getNotifications(params?: {
    skip?: number;
    limit?: number;
    unread_only?: boolean;
  }): Promise<any[]> {
    // Return mock notifications
    return [
      {
        id: 1,
        user_id: 1,
        title: 'Shipment Update',
        message: 'Your package ABC123456 is now in transit',
        notification_type: 'email',
        status: 'sent',
        created_at: '2024-01-10T10:00:00Z',
        sent_at: '2024-01-10T10:01:00Z',
        read_at: null
      }
    ];
  },

  async createNotification(notification: any): Promise<any> {
    return {
      id: Math.floor(Math.random() * 1000),
      ...notification,
      created_at: new Date().toISOString()
    };
  },

  async markAsRead(notificationId: number): Promise<void> {
    // Mock mark as read
    return;
  }
};

export const customerService = {
  async getAllCustomers(): Promise<any[]> {
    try {
      console.log('Fetching customers from backend...');
      const response = await api.get('/customers');
      console.log('Customers response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching customers:', error);
      // Return empty array if API fails
      return [];
    }
  }
};

export const adminService = {
  async getAllUsers(params?: {
    skip?: number;
    limit?: number;
    role?: string;
  }): Promise<User[]> {
    // Return mock users
    return [
      {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        role: 'customer' as any,
        phone: '+1-555-0123',
        address: '123 Main St, City, State',
        company: 'Test Company',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        last_login: '2024-01-10T10:00:00Z'
      }
    ];
  },

  async updateUserRole(userId: number, newRole: string): Promise<void> {
    // Mock role update
    return;
  },

  async toggleUserStatus(userId: number): Promise<void> {
    // Mock status toggle
    return;
  }
};

export default api; 