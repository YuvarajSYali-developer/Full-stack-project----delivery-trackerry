<template>
  <div class="app">
    <!-- Sidebar Navigation -->
    <aside v-if="isAuthenticated" class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">📦</div>
          <h2 class="logo-text">ShipTrack Pro</h2>
        </div>
        <NotificationBell />
      </div>

      <nav class="sidebar-nav">
        <router-link to="/dashboard" class="nav-item" active-class="active">
          <span class="nav-icon">📊</span>
          <span class="nav-text">Dashboard</span>
        </router-link>

        <router-link to="/shipments" class="nav-item" active-class="active">
          <span class="nav-icon">📦</span>
          <span class="nav-text">Shipments</span>
        </router-link>

        <router-link to="/tracking" class="nav-item" active-class="active">
          <span class="nav-icon">🔍</span>
          <span class="nav-text">Track Package</span>
        </router-link>

        <router-link to="/analytics" class="nav-item" active-class="active">
          <span class="nav-icon">📈</span>
          <span class="nav-text">Analytics</span>
        </router-link>

        <router-link to="/customers" class="nav-item" active-class="active">
          <span class="nav-icon">👥</span>
          <span class="nav-text">Customers</span>
        </router-link>

        <router-link to="/settings" class="nav-item" active-class="active">
          <span class="nav-icon">⚙️</span>
          <span class="nav-text">Settings</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <UserProfile />
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="main-content" :class="{ 'with-sidebar': isAuthenticated }">
      <router-view v-slot="{ Component }">
        <Transition name="page" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>

    <!-- Toast Notifications -->
    <ToastNotification />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { isAuthenticated as checkAuth } from './services/auth'
import UserProfile from './components/UserProfile.vue'
import NotificationBell from './components/NotificationBell.vue'
import ToastNotification from './components/ToastNotification.vue'

const router = useRouter()
const isAuthenticated = computed(() => checkAuth())
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app {
  min-height: 100vh;
  display: flex;
  background-color: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Sidebar Styles */
.sidebar {
  width: 280px;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow:
    4px 0 25px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset;
  backdrop-filter: blur(20px);
}

.sidebar-header {
  padding: 2rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.sidebar-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 1.5rem;
  right: 1.5rem;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  font-size: 2rem;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 16px;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow:
    0 8px 20px rgba(59, 130, 246, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  position: relative;
  overflow: hidden;
}

.logo-icon::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  background-size: 200% 200%;
  animation: gradient-shift 4s ease-in-out infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  color: #cbd5e1;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-left: 3px solid transparent;
  margin: 0.25rem 0.75rem;
  border-radius: 0 12px 12px 0;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s;
}

.nav-item:hover::before {
  left: 100%;
}

.nav-item:hover {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.15));
  color: white;
  border-left-color: #3b82f6;
  transform: translateX(4px);
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(139, 92, 246, 0.25));
  color: white;
  border-left-color: #3b82f6;
  transform: translateX(4px);
  box-shadow:
    0 4px 20px rgba(59, 130, 246, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
}

.nav-icon {
  font-size: 1.25rem;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-weight: 500;
  font-size: 0.95rem;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Main Content Styles */
.main-content {
  flex: 1;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  min-height: 100vh;
  position: relative;
}

.main-content::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.main-content > * {
  position: relative;
  z-index: 1;
}

.main-content.with-sidebar {
  margin-left: 280px;
}

/* Page Transitions */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .main-content.with-sidebar {
    margin-left: 0;
  }
}
</style>
