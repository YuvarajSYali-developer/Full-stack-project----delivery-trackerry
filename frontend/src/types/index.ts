// Enums
export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
  EMPLOYEE = 'employee',
  CUSTOMER = 'customer'
}

export enum ShipmentStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  PICKED_UP = 'picked_up',
  IN_TRANSIT = 'in_transit',
  OUT_FOR_DELIVERY = 'out_for_delivery',
  DELIVERED = 'delivered',
  CANCELLED = 'cancelled',
  RETURNED = 'returned'
}

export enum ShipmentPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  URGENT = 'urgent'
}

export enum NotificationType {
  EMAIL = 'email',
  SMS = 'sms',
  PUSH = 'push',
  IN_APP = 'in_app'
}

export enum NotificationStatus {
  PENDING = 'pending',
  SENT = 'sent',
  DELIVERED = 'delivered',
  FAILED = 'failed'
}

// User interfaces
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  phone?: string;
  address?: string;
  company?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface UserCreate {
  email: string;
  username: string;
  full_name?: string;
  role?: UserRole;
  phone?: string;
  address?: string;
  company?: string;
  password: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

// Shipment interfaces
export interface Shipment {
  id: number;
  tracking_number: string;
  status: ShipmentStatus;
  priority: ShipmentPriority;
  origin_address: string;
  destination_address: string;
  origin_city: string;
  destination_city: string;
  origin_country: string;
  destination_country: string;
  weight: number;
  dimensions?: string;
  declared_value?: number;
  insurance_required: boolean;
  fragile: boolean;
  description?: string;
  special_instructions?: string;
  estimated_delivery_date?: string;
  actual_delivery_date?: string;
  customer_id?: number;
  created_at: string;
  updated_at: string;
  customer?: User;
}

export interface ShipmentCreate {
  tracking_number?: string;
  status?: ShipmentStatus;
  priority?: ShipmentPriority;
  origin_address: string;
  destination_address: string;
  origin_city: string;
  destination_city: string;
  origin_country?: string;
  destination_country?: string;
  weight: number;
  dimensions?: string;
  declared_value?: number;
  insurance_required?: boolean;
  fragile?: boolean;
  description?: string;
  special_instructions?: string;
  estimated_delivery_date?: string;
  customer_id?: number;
}

export interface ShipmentUpdate {
  tracking_number?: string;
  status?: ShipmentStatus;
  priority?: ShipmentPriority;
  origin_address?: string;
  destination_address?: string;
  origin_city?: string;
  destination_city?: string;
  weight?: number;
  dimensions?: string;
  declared_value?: number;
  insurance_required?: boolean;
  fragile?: boolean;
  description?: string;
  special_instructions?: string;
  estimated_delivery_date?: string;
  actual_delivery_date?: string;
}

// Tracking interfaces
export interface TrackingHistory {
  id: number;
  shipment_id: number;
  status: ShipmentStatus;
  location: string;
  description: string;
  timestamp: string;
}

export interface TrackingHistoryCreate {
  status: ShipmentStatus;
  location: string;
  description: string;
  timestamp?: string;
}

// Notification interfaces
export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  notification_type: NotificationType;
  status: NotificationStatus;
  created_at: string;
  sent_at?: string;
  read_at?: string;
}

export interface NotificationCreate {
  user_id: number;
  title: string;
  message: string;
  notification_type: NotificationType;
  status?: NotificationStatus;
}

// Analytics interface
export interface DashboardAnalytics {
  total_shipments: number;
  pending_shipments: number;
  in_transit_shipments: number;
  delivered_shipments: number;
  total_revenue: number;
  monthly_revenue: number;
  average_delivery_time: number;
  customer_satisfaction: number;
  top_destinations: Array<{ city: string; count: number }>;
  recent_shipments: Array<{
    id: number;
    tracking_number: string;
    status: string;
    destination: string;
    created_at: string;
  }>;
}