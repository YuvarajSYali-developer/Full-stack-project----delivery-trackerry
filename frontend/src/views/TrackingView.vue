<template>
  <div class="tracking">
    <!-- Header -->
    <div class="tracking-header">
      <div class="header-content">
        <h1 class="page-title">Track Your Package</h1>
        <p class="page-subtitle">Enter your tracking number to get real-time updates on your shipment</p>
      </div>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <div class="search-card">
        <div class="search-form">
          <div class="input-group">
            <input
              v-model="trackingNumber"
              type="text"
              placeholder="Enter tracking number (e.g., ABC123456)"
              class="tracking-input"
              @keyup.enter="trackShipment"
            />
            <button @click="trackShipment" class="track-btn" :disabled="!trackingNumber || loading">
              <span v-if="loading" class="spinner"></span>
              <span v-else class="track-icon">🔍</span>
              {{ loading ? 'Tracking...' : 'Track' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      <div class="error-icon">⚠️</div>
      <div class="error-content">
        <h3>Tracking Error</h3>
        <p>{{ error }}</p>
      </div>
    </div>

    <!-- Tracking Results -->
    <div v-if="shipment" class="tracking-results">
      <!-- Shipment Info Card -->
      <div class="shipment-card">
        <div class="shipment-header">
          <div class="tracking-info">
            <h2 class="tracking-number">{{ shipment.tracking_number }}</h2>
            <div class="status-container">
              <span :class="['status-badge', `status-${shipment.status}`]">
                {{ formatStatus(shipment.status) }}
              </span>
            </div>
          </div>
          <div class="shipment-icon">📦</div>
        </div>
        
        <div class="shipment-details">
          <div class="detail-row">
            <div class="detail-item">
              <span class="detail-label">From</span>
              <span class="detail-value">{{ shipment.origin }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">To</span>
              <span class="detail-value">{{ shipment.destination }}</span>
            </div>
          </div>
          
          <div class="detail-row">
            <div class="detail-item">
              <span class="detail-label">Weight</span>
              <span class="detail-value">{{ shipment.weight }} kg</span>
            </div>
            <div class="detail-item" v-if="shipment.estimated_delivery">
              <span class="detail-label">Est. Delivery</span>
              <span class="detail-value">{{ formatDate(shipment.estimated_delivery) }}</span>
            </div>
          </div>
          
          <div v-if="shipment.description" class="detail-row">
            <div class="detail-item full-width">
              <span class="detail-label">Description</span>
              <span class="detail-value">{{ shipment.description }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Progress Timeline -->
      <div class="timeline-card">
        <div class="timeline-header">
          <h3 class="timeline-title">Tracking History</h3>
          <span class="timeline-subtitle">Follow your package journey</span>
        </div>
        
        <div class="timeline">
          <div v-for="(step, index) in trackingSteps" :key="index" 
               :class="['timeline-step', { 'completed': step.completed, 'current': step.current }]">
            <div class="step-indicator">
              <div class="step-icon">{{ step.icon }}</div>
            </div>
            <div class="step-content">
              <h4 class="step-title">{{ step.title }}</h4>
              <p class="step-description">{{ step.description }}</p>
              <span v-if="step.timestamp" class="step-time">{{ step.timestamp }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Info -->
      <div class="info-cards">
        <div class="info-card">
          <div class="info-icon">📍</div>
          <div class="info-content">
            <h4>Current Location</h4>
            <p>{{ getCurrentLocation() }}</p>
          </div>
        </div>
        
        <div class="info-card">
          <div class="info-icon">⏱️</div>
          <div class="info-content">
            <h4>Estimated Delivery</h4>
            <p>{{ getEstimatedDelivery() }}</p>
          </div>
        </div>
        
        <div class="info-card">
          <div class="info-icon">📞</div>
          <div class="info-content">
            <h4>Need Help?</h4>
            <p>Contact customer support</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Sample Tracking Numbers -->
    <div v-if="!shipment && !loading" class="sample-section">
      <div class="sample-card">
        <h3 class="sample-title">Try Sample Tracking Numbers</h3>
        <p class="sample-subtitle">Click on any tracking number below to see a demo</p>
        <div class="sample-numbers">
          <button v-for="sample in sampleNumbers" :key="sample" 
                  @click="trackingNumber = sample; trackShipment()" 
                  class="sample-btn">
            {{ sample }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { shipmentService } from '@/services/api'
import type { Shipment } from '@/types'

const trackingNumber = ref('')
const shipment = ref<Shipment | null>(null)
const loading = ref(false)
const error = ref('')

const sampleNumbers = ['ABC123456', 'DEF789012', 'GHI345678']

const trackingSteps = ref([
  {
    icon: '📋',
    title: 'Order Placed',
    description: 'Your shipment has been created and is being prepared',
    completed: true,
    current: false,
    timestamp: '2024-01-15 10:30 AM'
  },
  {
    icon: '📦',
    title: 'Package Picked Up',
    description: 'Package has been collected from the origin location',
    completed: true,
    current: false,
    timestamp: '2024-01-15 2:45 PM'
  },
  {
    icon: '🚛',
    title: 'In Transit',
    description: 'Your package is on its way to the destination',
    completed: true,
    current: true,
    timestamp: '2024-01-16 8:20 AM'
  },
  {
    icon: '🏪',
    title: 'Out for Delivery',
    description: 'Package is out for delivery to your address',
    completed: false,
    current: false,
    timestamp: null
  },
  {
    icon: '✅',
    title: 'Delivered',
    description: 'Package has been successfully delivered',
    completed: false,
    current: false,
    timestamp: null
  }
])

const trackShipment = async () => {
  if (!trackingNumber.value.trim()) return
  
  try {
    loading.value = true
    error.value = ''
    shipment.value = null
    
    const result = await shipmentService.trackShipment(trackingNumber.value.trim())
    shipment.value = result
    
    // Update tracking steps based on shipment status
    updateTrackingSteps(result.status)
    
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Shipment not found. Please check your tracking number.'
    shipment.value = null
  } finally {
    loading.value = false
  }
}

const updateTrackingSteps = (status: string) => {
  const statusMap: { [key: string]: number } = {
    'pending': 0,
    'shipped': 1,
    'in_transit': 2,
    'out_for_delivery': 3,
    'delivered': 4
  }
  
  const currentStep = statusMap[status] || 0
  
  trackingSteps.value.forEach((step, index) => {
    step.completed = index < currentStep
    step.current = index === currentStep
  })
}

const formatStatus = (status: string) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getCurrentLocation = () => {
  if (!shipment.value) return 'Unknown'
  
  const locationMap: { [key: string]: string } = {
    'pending': 'Origin facility',
    'shipped': 'In transit from origin',
    'in_transit': 'Distribution center',
    'out_for_delivery': 'Local delivery facility',
    'delivered': 'Delivered to destination'
  }
  
  return locationMap[shipment.value.status] || 'Unknown'
}

const getEstimatedDelivery = () => {
  if (!shipment.value) return 'Unknown'
  
  if (shipment.value.estimated_delivery) {
    return formatDate(shipment.value.estimated_delivery)
  }
  
  // Calculate estimated delivery based on current date
  const estimatedDate = new Date()
  estimatedDate.setDate(estimatedDate.getDate() + 3)
  return formatDate(estimatedDate.toISOString())
}
</script>

<style scoped>
.tracking {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.tracking-header {
  text-align: center;
  margin-bottom: 3rem;
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

.search-section {
  margin-bottom: 2rem;
}

.search-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.input-group {
  display: flex;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.tracking-input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.tracking-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.track-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.track-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.track-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.error-icon {
  font-size: 1.5rem;
}

.error-content h3 {
  color: #dc2626;
  margin-bottom: 0.25rem;
}

.error-content p {
  color: #991b1b;
  margin: 0;
}

.tracking-results {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.shipment-card, .timeline-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.shipment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
}

.tracking-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-pending { background: #fef3c7; color: #92400e; }
.status-shipped, .status-in_transit { background: #dbeafe; color: #1e40af; }
.status-delivered { background: #d1fae5; color: #065f46; }

.shipment-icon {
  font-size: 3rem;
}

.shipment-details {
  padding: 2rem;
}

.detail-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  display: block;
  font-weight: 600;
  color: #64748b;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.detail-value {
  display: block;
  color: #1e293b;
  font-weight: 500;
}

.timeline-header {
  padding: 2rem 2rem 1rem;
}

.timeline-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.timeline-subtitle {
  color: #64748b;
  font-size: 0.9rem;
}

.timeline {
  padding: 1rem 2rem 2rem;
}

.timeline-step {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  position: relative;
}

.timeline-step:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 20px;
  top: 40px;
  width: 2px;
  height: calc(100% + 1rem);
  background: #e2e8f0;
}

.timeline-step.completed::after {
  background: #3b82f6;
}

.step-indicator {
  flex-shrink: 0;
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  background: #f1f5f9;
  border: 2px solid #e2e8f0;
}

.timeline-step.completed .step-icon {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.timeline-step.current .step-icon {
  background: #fbbf24;
  border-color: #f59e0b;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.step-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.step-description {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.step-time {
  color: #94a3b8;
  font-size: 0.8rem;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.info-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
}

.info-content h4 {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.info-content p {
  color: #64748b;
  font-size: 0.9rem;
  margin: 0;
}

.sample-section {
  margin-top: 3rem;
}

.sample-card {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.sample-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.sample-subtitle {
  color: #64748b;
  margin-bottom: 1.5rem;
}

.sample-numbers {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.sample-btn {
  padding: 0.75rem 1.5rem;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  color: #3b82f6;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sample-btn:hover {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

@media (max-width: 768px) {
  .tracking {
    padding: 1rem;
  }
  
  .input-group {
    flex-direction: column;
  }
  
  .detail-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .sample-numbers {
    flex-direction: column;
    align-items: center;
  }
}
</style>
