<template>
  <div class="notification-bell" @click="toggleNotifications">
    <div class="bell-icon">
      🔔
      <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
    </div>
    
    <div v-if="showNotifications" class="notifications-dropdown">
      <div class="notifications-header">
        <h3>Notifications</h3>
        <button v-if="notifications.length > 0" @click="markAllAsRead" class="mark-all-read">
          Mark all as read
        </button>
      </div>
      
      <div class="notifications-list">
        <div v-if="notifications.length === 0" class="no-notifications">
          No new notifications
        </div>
        <div 
          v-for="notification in notifications" 
          :key="notification.id" 
          class="notification-item"
          :class="{ 'unread': !notification.read }"
          @click="markAsRead(notification.id)"
        >
          <div class="notification-icon">{{ getNotificationIcon(notification.type) }}</div>
          <div class="notification-content">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
          </div>
        </div>
      </div>
      
      <div class="notifications-footer">
        <router-link to="/notifications" @click="closeNotifications" class="view-all-link">
          View all notifications
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'NotificationBell',
  setup() {
    const showNotifications = ref(false)
    const notifications = ref([
      {
        id: 1,
        type: 'shipment',
        title: 'Shipment Update',
        message: 'Your package ABC123 has been delivered',
        created_at: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
        read: false
      },
      {
        id: 2,
        type: 'system',
        title: 'System Maintenance',
        message: 'Scheduled maintenance tonight at 2 AM',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
        read: false
      },
      {
        id: 3,
        type: 'shipment',
        title: 'New Shipment',
        message: 'Shipment XYZ789 has been created',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
        read: true
      }
    ])
    
    const unreadCount = computed(() => {
      return notifications.value.filter(n => !n.read).length
    })
    
    const toggleNotifications = () => {
      showNotifications.value = !showNotifications.value
    }
    
    const closeNotifications = () => {
      showNotifications.value = false
    }
    
    const markAsRead = (id) => {
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.read = true
      }
    }
    
    const markAllAsRead = () => {
      notifications.value.forEach(n => n.read = true)
    }
    
    const getNotificationIcon = (type) => {
      switch (type) {
        case 'shipment': return '📦'
        case 'system': return '⚙️'
        case 'alert': return '⚠️'
        default: return '📢'
      }
    }
    
    const formatTime = (date) => {
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / (1000 * 60))
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      
      if (minutes < 60) {
        return `${minutes}m ago`
      } else if (hours < 24) {
        return `${hours}h ago`
      } else {
        return `${days}d ago`
      }
    }
    
    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (!event.target.closest('.notification-bell')) {
        showNotifications.value = false
      }
    }
    
    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })
    
    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })
    
    return {
      showNotifications,
      notifications,
      unreadCount,
      toggleNotifications,
      closeNotifications,
      markAsRead,
      markAllAsRead,
      getNotificationIcon,
      formatTime
    }
  }
}
</script>

<style scoped>
.notification-bell {
  position: relative;
  cursor: pointer;
}

.bell-icon {
  position: relative;
  font-size: 1.5rem;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.bell-icon:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.notification-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.notifications-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 350px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-top: 0.5rem;
  overflow: hidden;
}

.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.notifications-header h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.mark-all-read {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 0.875rem;
  cursor: pointer;
  font-weight: 500;
}

.mark-all-read:hover {
  text-decoration: underline;
}

.notifications-list {
  max-height: 300px;
  overflow-y: auto;
}

.no-notifications {
  padding: 2rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
}

.notification-item {
  display: flex;
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f9fafb;
}

.notification-item.unread {
  background-color: #eff6ff;
  border-left: 3px solid #3b82f6;
}

.notification-icon {
  font-size: 1.25rem;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.notification-message {
  color: #6b7280;
  font-size: 0.8rem;
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.notification-time {
  color: #9ca3af;
  font-size: 0.75rem;
}

.notifications-footer {
  padding: 0.75rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  text-align: center;
}

.view-all-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.view-all-link:hover {
  text-decoration: underline;
}
</style>
