<template>
  <div class="min-h-screen flex flex-col">
    <!-- Main Content -->
    <div class="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <slot />
    </div>
    
    <!-- Footer -->
    <AppFooter />
  </div>
</template>

<script setup>
import AppFooter from '../components/AppFooter.vue'
</script> 