<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative">
    <!-- Global Background Elements -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse opacity-70"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-full blur-3xl animate-pulse opacity-70" style="animation-delay: 3s;"></div>
      <div class="absolute top-1/3 left-1/3 w-96 h-96 bg-gradient-to-br from-indigo-500/15 to-purple-500/15 rounded-full blur-3xl animate-pulse opacity-50" style="animation-delay: 6s;"></div>
    </div>
    
    <!-- Router View Container -->
    <div class="relative z-10">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'

const router = useRouter()
const authStore = useAuthStore()

onMounted(() => {
  // If the user is at the root path, redirect to the appropriate view
  // based on authentication status
  if (router.currentRoute.value.path === '/') {
    if (!authStore.isAuthenticated) {
      router.push('/home')
    }
    // If authenticated, they'll be directed to dashboard via the router guard
  }
})
</script>

<style>
/* Global Styles */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: transparent;
  color: #ffffff;
  overflow-x: hidden;
}

/* Custom Scrollbar for the entire app */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.2);
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #8b5cf6, #ec4899);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #7c3aed, #db2777);
}

/* Firefox scrollbar */
html {
  scrollbar-width: thin;
  scrollbar-color: #8b5cf6 rgba(15, 23, 42, 0.2);
}

/* Smooth scrolling for the entire app */
html {
  scroll-behavior: smooth;
}

/* Global animation for page transitions */
.page-enter-active,
.page-leave-active {
  transition: all 0.3s ease-in-out;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Global focus styles */
*:focus {
  outline: 2px solid #8b5cf6;
  outline-offset: 2px;
}

/* Selection styles */
::selection {
  background: rgba(139, 92, 246, 0.3);
  color: #ffffff;
}

::-moz-selection {
  background: rgba(139, 92, 246, 0.3);
  color: #ffffff;
}

/* Form elements styling to override global white text */
select {
  color: #374151 !important;
  background-color: #ffffff !important;
}

select option {
  color: #374151 !important;
  background-color: #ffffff !important;
}

input[type="text"],
input[type="email"],
input[type="password"],
input[type="date"],
input[type="number"],
textarea {
  color: #374151 !important;
  background-color: #ffffff !important;
}

input[type="text"]::placeholder,
input[type="email"]::placeholder,
input[type="password"]::placeholder,
textarea::placeholder {
  color: #9ca3af !important;
}
</style> 