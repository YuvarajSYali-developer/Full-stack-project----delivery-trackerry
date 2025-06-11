<template>
  <div class="shipments-container">
    <div class="header">
      <div class="header-left">
        <h1>Shipments</h1>
        <p class="header-subtitle">Manage your shipments efficiently</p>
      </div>
      <div class="header-right">
        <button @click="showCreateModal = true" class="btn-primary">
          <span class="btn-icon">+</span>
          Create New Shipment
        </button>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="quick-stats">
      <div class="stat-card">
        <div class="stat-number">{{ shipments.length }}</div>
        <div class="stat-label">Total Shipments</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ getStatusCount('in_transit') }}</div>
        <div class="stat-label">In Transit</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ getStatusCount('delivered') }}</div>
        <div class="stat-label">Delivered</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ getStatusCount('pending') }}</div>
        <div class="stat-label">Pending</div>
      </div>
    </div>

    <div v-if="loading" class="loading">
      Loading shipments...
    </div>
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    <div v-else class="shipments-list">
      <div v-for="shipment in shipments" :key="shipment.id" class="shipment-card">
        <div class="shipment-content">
          <h3>{{ shipment.tracking_number }}</h3>
          <p><strong>Origin:</strong> {{ shipment.origin }}</p>
          <p><strong>Destination:</strong> {{ shipment.destination }}</p>
          <p><strong>Weight:</strong> {{ shipment.weight }} kg</p>
          <p v-if="shipment.description"><strong>Description:</strong> {{ shipment.description }}</p>
          <p v-if="shipment.estimated_delivery"><strong>Est. Delivery:</strong> {{ new Date(shipment.estimated_delivery).toLocaleDateString() }}</p>
          <p><strong>Status:</strong> <span :class="'status-' + shipment.status">{{ shipment.status.replace('_', ' ') }}</span></p>
        </div>
        <div class="shipment-actions">
          <button @click="editShipment(shipment)" class="btn-edit">
            Edit
          </button>
          <button @click="deleteShipment(shipment.id)" class="btn-delete">
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="modal">
      <div class="modal-content">
        <h2>{{ editingShipment ? 'Edit Shipment' : 'Create Shipment' }}</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="tracking_number">Tracking Number</label>
            <input
              type="text"
              id="tracking_number"
              v-model="shipmentForm.tracking_number"
              required
              class="form-control"
              placeholder="e.g., ABC123456"
            />
          </div>
          <div class="form-group">
            <label for="origin">Origin</label>
            <input
              type="text"
              id="origin"
              v-model="shipmentForm.origin"
              required
              class="form-control"
              placeholder="e.g., New York"
            />
          </div>
          <div class="form-group">
            <label for="destination">Destination</label>
            <input
              type="text"
              id="destination"
              v-model="shipmentForm.destination"
              required
              class="form-control"
              placeholder="e.g., Los Angeles"
            />
          </div>
          <div class="form-group">
            <label for="weight">Weight (kg)</label>
            <input
              type="number"
              id="weight"
              v-model="shipmentForm.weight"
              required
              min="0.1"
              step="0.1"
              class="form-control"
            />
          </div>
          <div class="form-group">
            <label for="status">Status</label>
            <select
              id="status"
              v-model="shipmentForm.status"
              required
              class="form-control"
            >
              <option value="pending">Pending</option>
              <option value="shipped">Shipped</option>
              <option value="in_transit">In Transit</option>
              <option value="delivered">Delivered</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="form-group">
            <label for="description">Description (Optional)</label>
            <textarea
              id="description"
              v-model="shipmentForm.description"
              class="form-control"
              placeholder="Package description..."
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="estimated_delivery">Estimated Delivery (Optional)</label>
            <input
              type="datetime-local"
              id="estimated_delivery"
              v-model="shipmentForm.estimated_delivery"
              class="form-control"
            />
          </div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { shipmentService } from '@/services/api';
import type { Shipment } from '@/types';

const router = useRouter();
const shipments = ref<Shipment[]>([]);
const loading = ref(true);
const error = ref('');
const showCreateModal = ref(false);
const submitting = ref(false);
const editingShipment = ref<Shipment | null>(null);

const shipmentForm = ref({
  tracking_number: '',
  origin: '',
  destination: '',
  weight: 0,
  status: 'pending',
  description: '',
  estimated_delivery: ''
});

const loadShipments = async () => {
  try {
    loading.value = true;
    error.value = '';
    shipments.value = await shipmentService.getAllShipments();
  } catch (err) {
    error.value = 'Failed to load shipments';
  } finally {
    loading.value = false;
  }
};

const handleSubmit = async () => {
  try {
    submitting.value = true;
    if (editingShipment.value) {
      await shipmentService.updateShipment(editingShipment.value.id, shipmentForm.value);
    } else {
      await shipmentService.createShipment(shipmentForm.value);
    }
    await loadShipments();
    closeModal();
  } catch (err) {
    error.value = 'Failed to save shipment';
  } finally {
    submitting.value = false;
  }
};

const editShipment = (shipment: Shipment) => {
  editingShipment.value = shipment;
  shipmentForm.value = { ...shipment };
  showCreateModal.value = true;
};

const deleteShipment = async (id: number) => {
  if (!confirm('Are you sure you want to delete this shipment?')) return;
  
  try {
    await shipmentService.deleteShipment(id);
    await loadShipments();
  } catch (err) {
    error.value = 'Failed to delete shipment';
  }
};

const closeModal = () => {
  showCreateModal.value = false;
  editingShipment.value = null;
  shipmentForm.value = {
    tracking_number: '',
    origin: '',
    destination: '',
    weight: 0,
    status: 'pending',
    description: '',
    estimated_delivery: ''
  };
};

const getStatusCount = (status: string) => {
  return shipments.value.filter(shipment => shipment.status === status).length;
};

onMounted(() => {
  loadShipments();
});
</script>

<style scoped>
.shipments-container {
  padding: 1.5rem;
  background-color: #f8f9fa;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  color: #2c3e50;
  margin: 0 0 0.25rem 0;
  font-size: 2rem;
  font-weight: 600;
}

.header-subtitle {
  color: #6c757d;
  margin: 0;
  font-size: 1rem;
}

.header-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.btn-icon {
  font-size: 1.2rem;
  margin-right: 0.5rem;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #6c757d;
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.shipments-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.shipment-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid #e9ecef;
}

.shipment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.shipment-content {
  flex: 1;
}

.shipment-content h3 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 600;
}

.shipment-content p {
  margin: 0.5rem 0;
  color: #6c757d;
  font-size: 0.95rem;
}

.shipment-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-left: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.btn-edit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.btn-edit:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-delete {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.btn-delete:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-content h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: 600;
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
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #dc3545;
  text-align: center;
  padding: 1rem;
  background-color: #f8d7da;
  border-radius: 4px;
  margin: 1rem 0;
}

/* Status-specific styling */
.status-pending {
  color: #ffc107;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background-color: #fff3cd;
}

.status-shipped {
  color: #17a2b8;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background-color: #d1ecf1;
}

.status-delivered {
  color: #28a745;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background-color: #d4edda;
}

.status-in_transit {
  color: #fd7e14;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background-color: #fff3cd;
}

.status-cancelled {
  color: #dc3545;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background-color: #f8d7da;
}

textarea.form-control {
  resize: vertical;
  min-height: 80px;
}

.status-cancelled {
  color: #dc3545;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background-color: #f8d7da;
}
</style> 