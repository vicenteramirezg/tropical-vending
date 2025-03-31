<template>
  <div class="min-h-screen">
    <router-view />
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