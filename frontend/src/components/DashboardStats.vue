<template>
  <div class="dashboard-stats">
    <div class="stats-grid">
      <!-- Total Shipments Card -->
      <div class="stat-card total">
        <div class="stat-icon">
          <i class="icon-box">📦</i>
        </div>
        <div class="stat-content">
          <h3>{{ analytics?.total_shipments || 0 }}</h3>
          <p>Total Shipments</p>
        </div>
      </div>

      <!-- Status Cards -->
      <div class="stat-card pending">
        <div class="stat-icon">
          <i class="icon-clock">⏳</i>
        </div>
        <div class="stat-content">
          <h3>{{ analytics?.status_counts.pending || 0 }}</h3>
          <p>Pending</p>
        </div>
      </div>

      <div class="stat-card shipped">
        <div class="stat-icon">
          <i class="icon-truck">🚚</i>
        </div>
        <div class="stat-content">
          <h3>{{ analytics?.status_counts.shipped || 0 }}</h3>
          <p>Shipped</p>
        </div>
      </div>

      <div class="stat-card delivered">
        <div class="stat-icon">
          <i class="icon-check">✅</i>
        </div>
        <div class="stat-content">
          <h3>{{ analytics?.status_counts.delivered || 0 }}</h3>
          <p>Delivered</p>
        </div>
      </div>
    </div>

    <!-- Recent Shipments -->
    <div class="recent-shipments">
      <h3>Recent Shipments</h3>
      <div class="shipments-list">
        <div 
          v-for="shipment in analytics?.recent_shipments" 
          :key="shipment.id"
          class="shipment-item"
        >
          <div class="shipment-info">
            <span class="tracking-number">{{ shipment.tracking_number }}</span>
            <span class="route">{{ shipment.origin }} → {{ shipment.destination }}</span>
          </div>
          <div class="shipment-status">
            <span :class="['status-badge', shipment.status]">
              {{ shipment.status }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { shipmentService } from '../services/api'
import type { DashboardAnalytics } from '../types'

const analytics = ref<DashboardAnalytics | null>(null)
const loading = ref(true)
const error = ref('')

const loadAnalytics = async () => {
  try {
    loading.value = true
    analytics.value = await shipmentService.getDashboardAnalytics()
  } catch (err) {
    error.value = 'Failed to load analytics'
    console.error('Analytics error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAnalytics()
})
</script>

<style scoped>
.dashboard-stats {
  padding: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.total .stat-icon { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.pending .stat-icon { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.shipped .stat-icon { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.delivered .stat-icon { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-content h3 {
  font-size: 2rem;
  font-weight: bold;
  margin: 0;
  color: #2d3748;
}

.stat-content p {
  margin: 0;
  color: #718096;
  font-weight: 500;
}

.recent-shipments {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.recent-shipments h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
  font-size: 1.25rem;
}

.shipments-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.shipment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

.shipment-item:hover {
  background: #edf2f7;
}

.shipment-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.tracking-number {
  font-weight: 600;
  color: #2d3748;
}

.route {
  color: #718096;
  font-size: 0.875rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.pending {
  background: #fed7d7;
  color: #c53030;
}

.status-badge.shipped {
  background: #bee3f8;
  color: #2b6cb0;
}

.status-badge.in_transit {
  background: #faf089;
  color: #744210;
}

.status-badge.delivered {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.cancelled {
  background: #fed7d7;
  color: #c53030;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .shipment-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
