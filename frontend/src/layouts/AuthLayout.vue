<template>
  <div class="min-h-screen flex flex-col justify-between bg-gray-50">
    <div class="flex-grow flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div class="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Tropical Vending
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Vending Machine Management System
        </p>
      </div>

      <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div class="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <router-view />
        </div>
        
        <div class="mt-6 text-center">
          <router-link 
            to="/home" 
            class="text-primary-600 hover:text-primary-700 font-medium"
          >
            Back to home page
          </router-link>
        </div>
      </div>
    </div>
    
    <AppFooter />
  </div>
</template>

<script setup>
import AppFooter from '../components/AppFooter.vue'
</script> 