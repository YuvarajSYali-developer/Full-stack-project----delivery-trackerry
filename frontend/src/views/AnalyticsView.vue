<template>
  <div class="analytics">
    <!-- Header -->
    <div class="analytics-header">
      <div class="header-content">
        <h1 class="page-title">Analytics & Reports</h1>
        <p class="page-subtitle">Comprehensive insights into your shipment operations</p>
      </div>
      <div class="header-actions">
        <select v-model="selectedPeriod" class="period-select">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 3 months</option>
          <option value="365">Last year</option>
        </select>
        <button class="btn-export">
          <span class="btn-icon">📊</span>
          Export Report
        </button>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="metrics-grid">
      <div class="metric-card revenue">
        <div class="metric-icon">💰</div>
        <div class="metric-content">
          <h3 class="metric-value">₹{{ analytics.total_revenue?.toLocaleString() || '0' }}</h3>
          <p class="metric-label">Total Revenue</p>
          <span class="metric-change positive">+12.5%</span>
        </div>
      </div>

      <div class="metric-card shipments">
        <div class="metric-icon">📦</div>
        <div class="metric-content">
          <h3 class="metric-value">{{ analytics.total_shipments || 0 }}</h3>
          <p class="metric-label">Total Shipments</p>
          <span class="metric-change positive">+8.3%</span>
        </div>
      </div>

      <div class="metric-card delivery">
        <div class="metric-icon">⚡</div>
        <div class="metric-content">
          <h3 class="metric-value">{{ analytics.average_delivery_time || 0 }} days</h3>
          <p class="metric-label">Avg Delivery Time</p>
          <span class="metric-change negative">-0.3 days</span>
        </div>
      </div>

      <div class="metric-card satisfaction">
        <div class="metric-icon">⭐</div>
        <div class="metric-content">
          <h3 class="metric-value">{{ analytics.customer_satisfaction || 4.8 }}/5</h3>
          <p class="metric-label">Customer Rating</p>
          <span class="metric-change positive">+0.2</span>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-grid">
      <!-- Shipment Trends Chart -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">Shipment Trends</h3>
          <div class="chart-legend">
            <span class="legend-item">
              <span class="legend-color created"></span>
              Created
            </span>
            <span class="legend-item">
              <span class="legend-color delivered"></span>
              Delivered
            </span>
          </div>
        </div>
        <div class="chart-content">
          <div class="chart-placeholder">
            <div class="chart-bars">
              <div class="bar-group">
                <div class="bar created" style="height: 60%"></div>
                <div class="bar delivered" style="height: 45%"></div>
                <span class="bar-label">Mon</span>
              </div>
              <div class="bar-group">
                <div class="bar created" style="height: 80%"></div>
                <div class="bar delivered" style="height: 70%"></div>
                <span class="bar-label">Tue</span>
              </div>
              <div class="bar-group">
                <div class="bar created" style="height: 70%"></div>
                <div class="bar delivered" style="height: 65%"></div>
                <span class="bar-label">Wed</span>
              </div>
              <div class="bar-group">
                <div class="bar created" style="height: 90%"></div>
                <div class="bar delivered" style="height: 80%"></div>
                <span class="bar-label">Thu</span>
              </div>
              <div class="bar-group">
                <div class="bar created" style="height: 85%"></div>
                <div class="bar delivered" style="height: 75%"></div>
                <span class="bar-label">Fri</span>
              </div>
              <div class="bar-group">
                <div class="bar created" style="height: 50%"></div>
                <div class="bar delivered" style="height: 40%"></div>
                <span class="bar-label">Sat</span>
              </div>
              <div class="bar-group">
                <div class="bar created" style="height: 40%"></div>
                <div class="bar delivered" style="height: 35%"></div>
                <span class="bar-label">Sun</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Distribution -->
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">Status Distribution</h3>
        </div>
        <div class="chart-content">
          <div class="donut-chart">
            <div class="donut-center">
              <span class="donut-total">{{ analytics.total_shipments || 0 }}</span>
              <span class="donut-label">Total</span>
            </div>
          </div>
          <div class="status-legend">
            <div class="status-item">
              <span class="status-color pending"></span>
              <span class="status-text">Pending ({{ Math.round((analytics.pending_shipments / analytics.total_shipments) * 100) || 0 }}%)</span>
              <span class="status-count">{{ analytics.pending_shipments || 0 }}</span>
            </div>
            <div class="status-item">
              <span class="status-color transit"></span>
              <span class="status-text">In Transit ({{ Math.round((analytics.in_transit_shipments / analytics.total_shipments) * 100) || 0 }}%)</span>
              <span class="status-count">{{ analytics.in_transit_shipments || 0 }}</span>
            </div>
            <div class="status-item">
              <span class="status-color delivered"></span>
              <span class="status-text">Delivered ({{ Math.round((analytics.delivered_shipments / analytics.total_shipments) * 100) || 0 }}%)</span>
              <span class="status-count">{{ analytics.delivered_shipments || 0 }}</span>
            </div>
            <div class="status-item">
              <span class="status-color cancelled"></span>
              <span class="status-text">Cancelled (0%)</span>
              <span class="status-count">0</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Tables -->
    <div class="tables-grid">
      <!-- Top Destinations -->
      <div class="table-card">
        <div class="table-header">
          <h3 class="table-title">Top Destinations</h3>
        </div>
        <div class="table-content">
          <div class="destination-list">
            <div class="destination-item">
              <div class="destination-info">
                <span class="destination-name">Mumbai, Maharashtra</span>
                <span class="destination-count">12 shipments</span>
              </div>
              <div class="destination-bar">
                <div class="bar-fill" style="width: 100%"></div>
              </div>
            </div>
            <div class="destination-item">
              <div class="destination-info">
                <span class="destination-name">Delhi, NCR</span>
                <span class="destination-count">10 shipments</span>
              </div>
              <div class="destination-bar">
                <div class="bar-fill" style="width: 83%"></div>
              </div>
            </div>
            <div class="destination-item">
              <div class="destination-info">
                <span class="destination-name">Bangalore, Karnataka</span>
                <span class="destination-count">8 shipments</span>
              </div>
              <div class="destination-bar">
                <div class="bar-fill" style="width: 67%"></div>
              </div>
            </div>
            <div class="destination-item">
              <div class="destination-info">
                <span class="destination-name">Chennai, Tamil Nadu</span>
                <span class="destination-count">7 shipments</span>
              </div>
              <div class="destination-bar">
                <div class="bar-fill" style="width: 58%"></div>
              </div>
            </div>
            <div class="destination-item">
              <div class="destination-info">
                <span class="destination-name">Pune, Maharashtra</span>
                <span class="destination-count">6 shipments</span>
              </div>
              <div class="destination-bar">
                <div class="bar-fill" style="width: 50%"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Metrics -->
      <div class="table-card">
        <div class="table-header">
          <h3 class="table-title">Performance Metrics</h3>
        </div>
        <div class="table-content">
          <div class="metrics-list">
            <div class="metric-row">
              <span class="metric-name">On-time Delivery Rate</span>
              <span class="metric-value">94.2%</span>
              <span class="metric-trend positive">↗ +2.1%</span>
            </div>
            <div class="metric-row">
              <span class="metric-name">Average Processing Time</span>
              <span class="metric-value">4.2 hours</span>
              <span class="metric-trend positive">↗ -0.8h</span>
            </div>
            <div class="metric-row">
              <span class="metric-name">Customer Satisfaction</span>
              <span class="metric-value">4.8/5.0</span>
              <span class="metric-trend positive">↗ +0.2</span>
            </div>
            <div class="metric-row">
              <span class="metric-name">Return Rate</span>
              <span class="metric-value">2.1%</span>
              <span class="metric-trend positive">↗ -0.5%</span>
            </div>
            <div class="metric-row">
              <span class="metric-name">Cost per Shipment</span>
              <span class="metric-value">$19.70</span>
              <span class="metric-trend negative">↗ +$1.20</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { shipmentService } from '../services/api'

const selectedPeriod = ref('30')
const analytics = ref({
  total_shipments: 0,
  pending_shipments: 0,
  in_transit_shipments: 0,
  delivered_shipments: 0,
  total_revenue: 0,
  average_delivery_time: 0,
  customer_satisfaction: 4.8
})
const loading = ref(true)

// Fetch analytics data from backend
const fetchAnalytics = async () => {
  try {
    loading.value = true
    const data = await shipmentService.getDashboardAnalytics()
    analytics.value = data
    console.log('Analytics data loaded:', data)
  } catch (error) {
    console.error('Error fetching analytics:', error)
  } finally {
    loading.value = false
  }
}

// Load analytics on component mount
onMounted(() => {
  fetchAnalytics()
})
</script>

<style scoped>
.analytics {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.analytics-header {
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
  align-items: center;
}

.period-select {
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  font-weight: 500;
  cursor: pointer;
}

.btn-export {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-export:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.metric-card.revenue .metric-icon { background: linear-gradient(135deg, #10b981, #059669); }
.metric-card.shipments .metric-icon { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.metric-card.delivery .metric-icon { background: linear-gradient(135deg, #8b5cf6, #7c3aed); }
.metric-card.satisfaction .metric-icon { background: linear-gradient(135deg, #f59e0b, #d97706); }

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.metric-label {
  color: #64748b;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.metric-change {
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.metric-change.positive {
  background: #d1fae5;
  color: #065f46;
}

.metric-change.negative {
  background: #fee2e2;
  color: #991b1b;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-card, .table-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.chart-header, .table-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title, .table-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-color.created { background: #3b82f6; }
.legend-color.delivered { background: #10b981; }

.chart-content, .table-content {
  padding: 1.5rem;
}

.chart-bars {
  display: flex;
  align-items: end;
  justify-content: space-between;
  height: 200px;
  gap: 1rem;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.bar {
  width: 20px;
  border-radius: 4px 4px 0 0;
  margin: 0 2px;
}

.bar.created { background: #3b82f6; }
.bar.delivered { background: #10b981; }

.bar-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.donut-chart {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: conic-gradient(
    #f59e0b 0deg 54deg,
    #3b82f6 54deg 180deg,
    #10b981 180deg 342deg,
    #ef4444 342deg 360deg
  );
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  position: relative;
}

.donut-chart::before {
  content: '';
  width: 100px;
  height: 100px;
  background: white;
  border-radius: 50%;
  position: absolute;
}

.donut-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
}

.donut-total {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.donut-label {
  font-size: 0.875rem;
  color: #64748b;
}

.status-legend {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.status-color.pending { background: #f59e0b; }
.status-color.transit { background: #3b82f6; }
.status-color.delivered { background: #10b981; }
.status-color.cancelled { background: #ef4444; }

.status-text {
  flex: 1;
  font-size: 0.875rem;
  color: #64748b;
}

.status-count {
  font-weight: 600;
  color: #1e293b;
}

.tables-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.destination-list, .metrics-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.destination-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.destination-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.destination-name {
  font-weight: 600;
  color: #1e293b;
}

.destination-count {
  font-size: 0.875rem;
  color: #64748b;
}

.destination-bar {
  width: 100px;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 4px;
}

.metric-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.metric-row:last-child {
  border-bottom: none;
}

.metric-name {
  flex: 1;
  color: #64748b;
  font-size: 0.875rem;
}

.metric-row .metric-value {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.875rem;
}

.metric-trend {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.metric-trend.positive {
  background: #d1fae5;
  color: #065f46;
}

.metric-trend.negative {
  background: #fee2e2;
  color: #991b1b;
}

@media (max-width: 768px) {
  .analytics {
    padding: 1rem;
  }
  
  .analytics-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .charts-grid, .tables-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
