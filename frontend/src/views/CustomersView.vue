<template>
  <div class="customers">
    <!-- Header -->
    <div class="customers-header">
      <div class="header-content">
        <h1 class="page-title">Customer Management</h1>
        <p class="page-subtitle">Manage your customers and their shipping history</p>
      </div>
      <div class="header-actions">
        <button class="btn-primary">
          <span class="btn-icon">👤</span>
          Add Customer
        </button>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="search-section">
      <div class="search-card">
        <div class="search-controls">
          <div class="search-input-group">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search customers by name, email, or company..."
              class="search-input"
            />
            <button class="search-btn">
              <span class="search-icon">🔍</span>
            </button>
          </div>
          <div class="filter-controls">
            <select v-model="statusFilter" class="filter-select">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            <select v-model="sortBy" class="filter-select">
              <option value="name">Sort by Name</option>
              <option value="email">Sort by Email</option>
              <option value="shipments">Sort by Shipments</option>
              <option value="joined">Sort by Join Date</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Customer Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ customers.length }}</h3>
          <p class="stat-label">Total Customers</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ customers.filter(c => c.status === 'active').length }}</h3>
          <p class="stat-label">Active Customers</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">📦</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ customers.length > 0 ? (customers.reduce((sum, c) => sum + c.shipmentCount, 0) / customers.length).toFixed(1) : '0' }}</h3>
          <p class="stat-label">Avg Shipments/Customer</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-content">
          <h3 class="stat-number">₹{{ customers.length > 0 ? Math.round(customers.reduce((sum, c) => sum + c.totalValue, 0) / customers.length) : '0' }}</h3>
          <p class="stat-label">Avg Customer Value</p>
        </div>
      </div>
    </div>

    <!-- Customers Table -->
    <div class="customers-table-card">
      <div class="table-header">
        <h3 class="table-title">Customer Directory</h3>
        <div class="table-actions">
          <button class="btn-secondary">
            <span class="btn-icon">📊</span>
            Export
          </button>
        </div>
      </div>
      
      <div class="table-content">
        <div class="table-wrapper">
          <table class="customers-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Contact</th>
                <th>Company</th>
                <th>Shipments</th>
                <th>Total Value</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="customer in filteredCustomers" :key="customer.id" class="customer-row">
                <td>
                  <div class="customer-info">
                    <div class="customer-avatar">{{ customer.name.charAt(0) }}</div>
                    <div class="customer-details">
                      <span class="customer-name">{{ customer.name }}</span>
                      <span class="customer-id">#{{ customer.id }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="contact-info">
                    <span class="customer-email">{{ customer.email }}</span>
                    <span class="customer-phone">{{ customer.phone }}</span>
                  </div>
                </td>
                <td>
                  <span class="customer-company">{{ customer.company }}</span>
                </td>
                <td>
                  <span class="shipment-count">{{ customer.shipmentCount }}</span>
                </td>
                <td>
                  <span class="customer-value">${{ customer.totalValue.toLocaleString() }}</span>
                </td>
                <td>
                  <span :class="['status-badge', customer.status]">
                    {{ customer.status }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="action-btn view" @click="viewCustomer(customer)">
                      <span class="action-icon">👁️</span>
                    </button>
                    <button class="action-btn edit" @click="editCustomer(customer)">
                      <span class="action-icon">✏️</span>
                    </button>
                    <button class="action-btn delete" @click="deleteCustomer(customer)">
                      <span class="action-icon">🗑️</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Customer Details Modal -->
    <div v-if="selectedCustomer" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">Customer Details</h2>
          <button @click="selectedCustomer = null" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <div class="customer-profile">
            <div class="profile-header">
              <div class="profile-avatar">{{ selectedCustomer.name.charAt(0) }}</div>
              <div class="profile-info">
                <h3 class="profile-name">{{ selectedCustomer.name }}</h3>
                <p class="profile-email">{{ selectedCustomer.email }}</p>
                <span :class="['status-badge', selectedCustomer.status]">
                  {{ selectedCustomer.status }}
                </span>
              </div>
            </div>
            
            <div class="profile-details">
              <div class="detail-section">
                <h4 class="section-title">Contact Information</h4>
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="detail-label">Phone</span>
                    <span class="detail-value">{{ selectedCustomer.phone }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Company</span>
                    <span class="detail-value">{{ selectedCustomer.company }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Address</span>
                    <span class="detail-value">{{ selectedCustomer.address }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Joined</span>
                    <span class="detail-value">{{ selectedCustomer.joinDate }}</span>
                  </div>
                </div>
              </div>
              
              <div class="detail-section">
                <h4 class="section-title">Shipping Statistics</h4>
                <div class="stats-row">
                  <div class="stat-item">
                    <span class="stat-value">{{ selectedCustomer.shipmentCount }}</span>
                    <span class="stat-label">Total Shipments</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">${{ selectedCustomer.totalValue.toLocaleString() }}</span>
                    <span class="stat-label">Total Value</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-value">${{ selectedCustomer.avgValue }}</span>
                    <span class="stat-label">Avg per Shipment</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-secondary" @click="selectedCustomer = null">Close</button>
          <button class="btn-primary" @click="editCustomer(selectedCustomer)">Edit Customer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { customerService } from '../services/api'

const searchQuery = ref('')
const statusFilter = ref('')
const sortBy = ref('name')
const selectedCustomer = ref(null)
const customers = ref([])
const loading = ref(true)

// Fetch customers from backend
const fetchCustomers = async () => {
  try {
    loading.value = true
    const backendCustomers = await customerService.getAllCustomers()

    // Transform backend data to match frontend interface
    customers.value = backendCustomers.map((customer: any) => ({
      id: customer.id,
      name: customer.name,
      email: customer.email,
      phone: customer.phone,
      company: customer.company,
      address: `${customer.address}, ${customer.city}`,
      shipmentCount: Math.floor(Math.random() * 30) + 5, // Random for now
      totalValue: Math.floor(Math.random() * 8000) + 2000, // Random for now
      avgValue: Math.floor(Math.random() * 200) + 150, // Random for now
      status: customer.is_active ? 'active' : 'inactive',
      joinDate: new Date(customer.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }))
  } catch (error) {
    console.error('Error fetching customers:', error)
    // Fallback to empty array
    customers.value = []
  } finally {
    loading.value = false
  }
}

// Load customers on component mount
onMounted(() => {
  fetchCustomers()
})

const filteredCustomers = computed(() => {
  let filtered = customers.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(customer =>
      customer.name.toLowerCase().includes(query) ||
      customer.email.toLowerCase().includes(query) ||
      customer.company.toLowerCase().includes(query)
    )
  }

  // Apply status filter
  if (statusFilter.value) {
    filtered = filtered.filter(customer => customer.status === statusFilter.value)
  }

  // Apply sorting
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'name':
        return a.name.localeCompare(b.name)
      case 'email':
        return a.email.localeCompare(b.email)
      case 'shipments':
        return b.shipmentCount - a.shipmentCount
      case 'joined':
        return new Date(b.joinDate).getTime() - new Date(a.joinDate).getTime()
      default:
        return 0
    }
  })

  return filtered
})

const viewCustomer = (customer: any) => {
  selectedCustomer.value = customer
}

const editCustomer = (customer: any) => {
  console.log('Edit customer:', customer)
  // Implement edit functionality
}

const deleteCustomer = (customer: any) => {
  if (confirm(`Are you sure you want to delete ${customer.name}?`)) {
    const index = customers.value.findIndex(c => c.id === customer.id)
    if (index > -1) {
      customers.value.splice(index, 1)
    }
  }
}
</script>

<style scoped>
.customers {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.customers-header {
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
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #f8fafc;
  color: #64748b;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.search-section {
  margin-bottom: 2rem;
}

.search-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input-group {
  flex: 1;
  display: flex;
  gap: 0.5rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.search-btn {
  padding: 0.75rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.filter-controls {
  display: flex;
  gap: 1rem;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
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

.customers-table-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.table-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.table-content {
  overflow-x: auto;
}

.customers-table {
  width: 100%;
  border-collapse: collapse;
}

.customers-table th {
  padding: 1rem 1.5rem;
  text-align: left;
  font-weight: 600;
  color: #64748b;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.customers-table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.customer-row:hover {
  background: #f8fafc;
}

.customer-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.customer-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
}

.customer-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.customer-name {
  font-weight: 600;
  color: #1e293b;
}

.customer-id {
  font-size: 0.875rem;
  color: #64748b;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.customer-email {
  color: #1e293b;
}

.customer-phone {
  font-size: 0.875rem;
  color: #64748b;
}

.status-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.active {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.inactive {
  background: #fee2e2;
  color: #991b1b;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.action-btn.view {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.edit {
  background: #fef3c7;
  color: #92400e;
}

.action-btn.delete {
  background: #fee2e2;
  color: #991b1b;
}

.action-btn:hover {
  transform: scale(1.1);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f1f5f9;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.25rem;
  color: #64748b;
}

.modal-body {
  padding: 1.5rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  font-weight: 600;
}

.profile-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.profile-email {
  color: #64748b;
  margin-bottom: 0.5rem;
}

.detail-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
}

.detail-value {
  color: #1e293b;
}

.stats-row {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-item .stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.stat-item .stat-label {
  font-size: 0.875rem;
  color: #64748b;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

@media (max-width: 768px) {
  .customers {
    padding: 1rem;
  }
  
  .customers-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-controls {
    flex-direction: column;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-row {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
