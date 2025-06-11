<template>
  <div class="dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Welcome back! Here's what's happening with your shipments.</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="refreshData">
          <span class="btn-icon">🔄</span>
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">📦</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ stats.totalShipments }}</h3>
          <p class="stat-label">Total Shipments</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon pending">⏳</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ stats.pendingShipments }}</h3>
          <p class="stat-label">Pending</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon transit">🚛</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ stats.inTransitShipments }}</h3>
          <p class="stat-label">In Transit</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon delivered">✅</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ stats.deliveredShipments }}</h3>
          <p class="stat-label">Delivered</p>
        </div>
      </div>
    </div>

    <!-- Charts and Recent Activity -->
    <div class="dashboard-grid">
      <!-- Recent Shipments -->
      <div class="dashboard-card">
        <div class="card-header">
          <h2 class="card-title">Recent Shipments</h2>
          <router-link to="/shipments" class="view-all-link">View All</router-link>
        </div>
        <div class="card-content">
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>Loading shipments...</p>
          </div>
          <div v-else-if="recentShipments.length === 0" class="empty-state">
            <div class="empty-icon">📦</div>
            <p>No shipments found</p>
          </div>
          <div v-else class="shipments-list">
            <div v-for="shipment in recentShipments" :key="shipment.id" class="shipment-item">
              <div class="shipment-info">
                <h4 class="tracking-number">{{ shipment.tracking_number }}</h4>
                <p class="shipment-route">{{ shipment.origin }} → {{ shipment.destination }}</p>
              </div>
              <div class="shipment-status">
                <span :class="['status-badge', `status-${shipment.status}`]">
                  {{ formatStatus(shipment.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="dashboard-card">
        <div class="card-header">
          <h2 class="card-title">Quick Actions</h2>
        </div>
        <div class="card-content">
          <div class="quick-actions">
            <router-link to="/shipments" class="action-item">
              <div class="action-icon">📦</div>
              <div class="action-content">
                <h4>Create Shipment</h4>
                <p>Add a new shipment to track</p>
              </div>
            </router-link>
            
            <router-link to="/tracking" class="action-item">
              <div class="action-icon">🔍</div>
              <div class="action-content">
                <h4>Track Package</h4>
                <p>Search by tracking number</p>
              </div>
            </router-link>
            
            <router-link to="/analytics" class="action-item">
              <div class="action-icon">📊</div>
              <div class="action-content">
                <h4>View Analytics</h4>
                <p>Detailed reports and insights</p>
              </div>
            </router-link>
            
            <router-link to="/customers" class="action-item">
              <div class="action-icon">👥</div>
              <div class="action-content">
                <h4>Manage Customers</h4>
                <p>Customer information and history</p>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Activity Timeline -->
    <div class="dashboard-card">
      <div class="card-header">
        <h2 class="card-title">Recent Activity</h2>
      </div>
      <div class="card-content">
        <div class="activity-timeline">
          <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
            <div class="activity-icon">{{ activity.icon }}</div>
            <div class="activity-content">
              <h4 class="activity-title">{{ activity.title }}</h4>
              <p class="activity-description">{{ activity.description }}</p>
              <span class="activity-time">{{ activity.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { shipmentService } from '@/services/api'
import type { Shipment } from '@/types'

const loading = ref(true)
const recentShipments = ref<Shipment[]>([])

const stats = ref({
  totalShipments: 0,
  pendingShipments: 0,
  inTransitShipments: 0,
  deliveredShipments: 0
})

const recentActivity = ref([
  {
    id: 1,
    icon: '📦',
    title: 'New shipment created',
    description: 'Shipment ABC123456 has been created and is pending pickup',
    time: '2 minutes ago'
  },
  {
    id: 2,
    icon: '🚛',
    title: 'Shipment in transit',
    description: 'Shipment DEF789012 is now in transit to Los Angeles',
    time: '15 minutes ago'
  },
  {
    id: 3,
    icon: '✅',
    title: 'Delivery completed',
    description: 'Shipment GHI345678 has been successfully delivered',
    time: '1 hour ago'
  },
  {
    id: 4,
    icon: '👤',
    title: 'New customer registered',
    description: 'John Doe has registered as a new customer',
    time: '2 hours ago'
  }
])

const loadDashboardData = async () => {
  try {
    loading.value = true
    const shipments = await shipmentService.getAllShipments()
    
    // Calculate stats
    stats.value.totalShipments = shipments.length
    stats.value.pendingShipments = shipments.filter(s => s.status === 'pending').length
    stats.value.inTransitShipments = shipments.filter(s => s.status === 'in_transit' || s.status === 'shipped').length
    stats.value.deliveredShipments = shipments.filter(s => s.status === 'delivered').length
    
    // Get recent shipments (last 5)
    recentShipments.value = shipments.slice(0, 5)
    
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadDashboardData()
}

const formatStatus = (status: string) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.btn-icon {
  font-size: 1.1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  padding: 2rem;
  border-radius: 20px;
  box-shadow:
    0 10px 30px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.stat-card:hover::before {
  left: 100%;
}

.stat-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.3) inset;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.stat-icon::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: icon-shimmer 3s infinite;
}

@keyframes icon-shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.stat-icon.total {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}
.stat-icon.pending {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
}
.stat-icon.transit {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4);
}
.stat-icon.delivered {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: #64748b;
  font-weight: 500;
  margin: 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.dashboard-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow:
    0 10px 30px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.dashboard-card:hover {
  transform: translateY(-2px);
  box-shadow:
    0 15px 40px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.3) inset;
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.view-all-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
}

.view-all-link:hover {
  text-decoration: underline;
}

.card-content {
  padding: 1.5rem;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  color: #64748b;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f1f5f9;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.shipments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.shipment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
  transition: background-color 0.2s ease;
}

.shipment-item:hover {
  background: #f1f5f9;
}

.tracking-number {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.shipment-route {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

.status-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending { background: #fef3c7; color: #92400e; }
.status-shipped, .status-in_transit { background: #dbeafe; color: #1e40af; }
.status-delivered { background: #d1fae5; color: #065f46; }

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
}

.action-item:hover {
  background: #f1f5f9;
  transform: translateY(-1px);
}

.action-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.action-content h4 {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.action-content p {
  color: #64748b;
  font-size: 0.85rem;
  margin: 0;
}

.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.activity-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.activity-description {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.activity-time {
  color: #94a3b8;
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>
