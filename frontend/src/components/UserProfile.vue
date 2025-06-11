<template>
  <div class="user-profile">
    <div class="profile-info" @click="toggleDropdown">
      <div class="avatar">
        <span>{{ userInitials }}</span>
      </div>
      <div class="user-details">
        <div class="username">{{ user.username || 'User' }}</div>
        <div class="user-role">{{ user.role || 'Customer' }}</div>
      </div>
      <div class="dropdown-arrow" :class="{ 'rotated': showDropdown }">
        ▼
      </div>
    </div>
    
    <div v-if="showDropdown" class="dropdown-menu">
      <router-link to="/settings" class="dropdown-item" @click="closeDropdown">
        <span class="dropdown-icon">⚙️</span>
        Settings
      </router-link>
      <div class="dropdown-divider"></div>
      <button @click="logout" class="dropdown-item logout-btn">
        <span class="dropdown-icon">🚪</span>
        Logout
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'UserProfile',
  setup() {
    const router = useRouter()
    const showDropdown = ref(false)
    const user = ref({
      username: '',
      email: '',
      role: 'Customer'
    })
    
    const userInitials = computed(() => {
      if (user.value.username) {
        return user.value.username.substring(0, 2).toUpperCase()
      }
      return 'U'
    })
    
    const toggleDropdown = () => {
      showDropdown.value = !showDropdown.value
    }
    
    const closeDropdown = () => {
      showDropdown.value = false
    }
    
    const logout = () => {
      localStorage.removeItem('token')
      router.push('/login')
    }
    
    const loadUserProfile = async () => {
      try {
        const response = await api.get('/users/me')
        user.value = response.data
      } catch (error) {
        console.error('Error loading user profile:', error)
        // If we can't load the profile, we might have an invalid token
        if (error.response?.status === 401) {
          logout()
        }
      }
    }
    
    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (!event.target.closest('.user-profile')) {
        showDropdown.value = false
      }
    }
    
    onMounted(() => {
      loadUserProfile()
      document.addEventListener('click', handleClickOutside)
    })
    
    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })
    
    return {
      user,
      userInitials,
      showDropdown,
      toggleDropdown,
      closeDropdown,
      logout
    }
  }
}
</script>

<style scoped>
.user-profile {
  position: relative;
}

.profile-info {
  display: flex;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.profile-info::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s;
}

.profile-info:hover::before {
  left: 100%;
}

.profile-info:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.1));
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1rem;
  margin-right: 1rem;
  box-shadow:
    0 4px 15px rgba(59, 130, 246, 0.3),
    0 0 0 2px rgba(255, 255, 255, 0.2) inset;
  position: relative;
  overflow: hidden;
}

.avatar::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: avatar-shimmer 3s infinite;
}

@keyframes avatar-shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-weight: 600;
  color: white;
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  text-transform: capitalize;
}

.dropdown-arrow {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  transition: transform 0.2s;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
  margin-bottom: 0.75rem;
  overflow: hidden;
  z-index: 1000;
  animation: dropdown-appear 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

@keyframes dropdown-appear {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 1rem 1.25rem;
  color: #1e293b;
  text-decoration: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  position: relative;
  overflow: hidden;
}

.dropdown-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
  transition: left 0.3s;
}

.dropdown-item:hover::before {
  left: 100%;
}

.dropdown-item:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.05));
  transform: translateX(4px);
}

.dropdown-icon {
  margin-right: 0.5rem;
  font-size: 1rem;
}

.dropdown-divider {
  height: 1px;
  background-color: #e5e7eb;
  margin: 0.25rem 0;
}

.logout-btn {
  color: #dc2626;
}

.logout-btn:hover {
  background-color: #fef2f2;
}
</style>
