<template>
  <div class="settings-view">
    <div class="settings-header">
      <h1>Settings</h1>
      <p>Manage your account and application preferences</p>
    </div>

    <div class="settings-content">
      <!-- Profile Settings -->
      <div class="settings-section">
        <div class="section-header">
          <h2>Profile Settings</h2>
          <p>Update your personal information</p>
        </div>
        
        <div class="settings-card">
          <form @submit.prevent="updateProfile" class="profile-form">
            <div class="form-row">
              <div class="form-group">
                <label for="fullName">Full Name</label>
                <input 
                  type="text" 
                  id="fullName" 
                  v-model="profile.fullName"
                  placeholder="Enter your full name"
                />
              </div>
              <div class="form-group">
                <label for="email">Email</label>
                <input 
                  type="email" 
                  id="email" 
                  v-model="profile.email"
                  placeholder="Enter your email"
                />
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="phone">Phone</label>
                <input 
                  type="tel" 
                  id="phone" 
                  v-model="profile.phone"
                  placeholder="Enter your phone number"
                />
              </div>
              <div class="form-group">
                <label for="company">Company</label>
                <input 
                  type="text" 
                  id="company" 
                  v-model="profile.company"
                  placeholder="Enter your company name"
                />
              </div>
            </div>
            
            <div class="form-group">
              <label for="address">Address</label>
              <textarea 
                id="address" 
                v-model="profile.address"
                placeholder="Enter your address"
                rows="3"
              ></textarea>
            </div>
            
            <button type="submit" class="btn-primary" :disabled="updating">
              <span v-if="updating">Updating...</span>
              <span v-else>Update Profile</span>
            </button>
          </form>
        </div>
      </div>

      <!-- Security Settings -->
      <div class="settings-section">
        <div class="section-header">
          <h2>Security Settings</h2>
          <p>Manage your password and security preferences</p>
        </div>
        
        <div class="settings-card">
          <form @submit.prevent="changePassword" class="password-form">
            <div class="form-group">
              <label for="currentPassword">Current Password</label>
              <input 
                type="password" 
                id="currentPassword" 
                v-model="passwordForm.currentPassword"
                placeholder="Enter current password"
              />
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="newPassword">New Password</label>
                <input 
                  type="password" 
                  id="newPassword" 
                  v-model="passwordForm.newPassword"
                  placeholder="Enter new password"
                />
              </div>
              <div class="form-group">
                <label for="confirmPassword">Confirm Password</label>
                <input 
                  type="password" 
                  id="confirmPassword" 
                  v-model="passwordForm.confirmPassword"
                  placeholder="Confirm new password"
                />
              </div>
            </div>
            
            <button type="submit" class="btn-primary" :disabled="changingPassword">
              <span v-if="changingPassword">Changing...</span>
              <span v-else>Change Password</span>
            </button>
          </form>
        </div>
      </div>

      <!-- Notification Settings -->
      <div class="settings-section">
        <div class="section-header">
          <h2>Notification Settings</h2>
          <p>Configure how you receive notifications</p>
        </div>
        
        <div class="settings-card">
          <div class="notification-options">
            <div class="notification-item">
              <div class="notification-info">
                <h3>Email Notifications</h3>
                <p>Receive updates about your shipments via email</p>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" v-model="notifications.email">
                <span class="slider"></span>
              </label>
            </div>
            
            <div class="notification-item">
              <div class="notification-info">
                <h3>SMS Notifications</h3>
                <p>Get text messages for important shipment updates</p>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" v-model="notifications.sms">
                <span class="slider"></span>
              </label>
            </div>
            
            <div class="notification-item">
              <div class="notification-info">
                <h3>Push Notifications</h3>
                <p>Receive browser notifications for real-time updates</p>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" v-model="notifications.push">
                <span class="slider"></span>
              </label>
            </div>
            
            <div class="notification-item">
              <div class="notification-info">
                <h3>Marketing Communications</h3>
                <p>Receive promotional emails and updates</p>
              </div>
              <label class="toggle-switch">
                <input type="checkbox" v-model="notifications.marketing">
                <span class="slider"></span>
              </label>
            </div>
          </div>
          
          <button @click="updateNotifications" class="btn-primary" :disabled="updatingNotifications">
            <span v-if="updatingNotifications">Saving...</span>
            <span v-else>Save Notification Settings</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'SettingsView',
  setup() {
    const router = useRouter()
    
    const profile = ref({
      fullName: '',
      email: '',
      phone: '',
      company: '',
      address: ''
    })
    
    const passwordForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const notifications = ref({
      email: true,
      sms: false,
      push: true,
      marketing: false
    })
    
    const updating = ref(false)
    const changingPassword = ref(false)
    const updatingNotifications = ref(false)
    
    const loadProfile = async () => {
      try {
        const response = await api.get('/users/me')
        const user = response.data
        profile.value = {
          fullName: user.full_name || '',
          email: user.email || '',
          phone: user.phone || '',
          company: user.company || '',
          address: user.address || ''
        }
      } catch (error) {
        console.error('Error loading profile:', error)
      }
    }
    
    const updateProfile = async () => {
      updating.value = true
      try {
        await api.put('/users/me', {
          full_name: profile.value.fullName,
          email: profile.value.email,
          phone: profile.value.phone,
          company: profile.value.company,
          address: profile.value.address
        })
        alert('Profile updated successfully!')
      } catch (error) {
        console.error('Error updating profile:', error)
        alert('Error updating profile. Please try again.')
      } finally {
        updating.value = false
      }
    }
    
    const changePassword = async () => {
      if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
        alert('New passwords do not match!')
        return
      }
      
      changingPassword.value = true
      try {
        await api.put('/users/change-password', {
          current_password: passwordForm.value.currentPassword,
          new_password: passwordForm.value.newPassword
        })
        alert('Password changed successfully!')
        passwordForm.value = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
      } catch (error) {
        console.error('Error changing password:', error)
        alert('Error changing password. Please check your current password.')
      } finally {
        changingPassword.value = false
      }
    }
    
    const updateNotifications = async () => {
      updatingNotifications.value = true
      try {
        await api.put('/users/notifications', notifications.value)
        alert('Notification settings saved!')
      } catch (error) {
        console.error('Error updating notifications:', error)
        alert('Error saving notification settings.')
      } finally {
        updatingNotifications.value = false
      }
    }
    
    onMounted(() => {
      loadProfile()
    })
    
    return {
      profile,
      passwordForm,
      notifications,
      updating,
      changingPassword,
      updatingNotifications,
      updateProfile,
      changePassword,
      updateNotifications
    }
  }
}
</script>

<style scoped>
.settings-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.settings-header {
  margin-bottom: 2rem;
}

.settings-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.settings-header p {
  color: #6b7280;
  font-size: 1rem;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.settings-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.section-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.section-header h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.section-header p {
  color: #6b7280;
  font-size: 0.875rem;
}

.settings-card {
  padding: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.notification-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.notification-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

.notification-info h3 {
  font-size: 1rem;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.notification-info p {
  font-size: 0.875rem;
  color: #6b7280;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #3b82f6;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

@media (max-width: 768px) {
  .settings-view {
    padding: 1rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .notification-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
