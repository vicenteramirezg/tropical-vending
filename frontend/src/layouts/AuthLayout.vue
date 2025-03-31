<template>
  <div class="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-gray-50">
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
    
    <footer class="bg-white py-4 border-t border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p class="text-center text-gray-500 text-sm">
          Made with <span class="text-yellow-500">💛</span> by <a href="https://garat.dev" target="_blank" class="text-primary-600 hover:text-primary-700">Garat.dev</a>
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
// Auth layout is a simple container for auth pages
</script> 