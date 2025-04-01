<template>
  <div class="bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <!-- Hero Section -->
    <div class="relative overflow-hidden">
      <!-- Background Pattern -->
      <div class="absolute inset-0 z-0 opacity-10">
        <div class="absolute inset-0 bg-grid-primary-700/20 bg-[size:20px_20px]"></div>
      </div>
      
      <!-- Navigation -->
      <div class="relative z-10">
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div class="flex h-20 items-center justify-between">
            <div class="flex items-center">
              <div class="text-primary-700 text-2xl font-bold flex items-center">
                <img src="../assets/images/logo.png" alt="Tropical Vending Logo" class="h-10 w-auto mr-2" />
                Tropical Vending
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <template v-if="isAuthenticated">
                <router-link
                  to="/"
                  class="text-primary-600 hover:text-primary-700 font-medium"
                >
                  Dashboard
                </router-link>
                <button
                  @click="handleLogout"
                  class="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                >
                  Logout
                </button>
              </template>
              <template v-else>
                <router-link
                  to="/login"
                  class="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
                >
                  Login
                </router-link>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Hero Content -->
      <div class="relative z-10 mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
        <div class="lg:grid lg:grid-cols-12 lg:gap-8">
          <div class="lg:col-span-6">
            <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
              <span class="block">Manage Your</span>
              <span class="block text-primary-600">Vending Empire</span>
            </h1>
            <p class="mt-6 text-lg text-gray-600">
              Tropical Vending is a comprehensive platform for managing all aspects of your vending machine business - from locations and machines to inventory and analytics.
            </p>
            <div class="mt-10 flex items-center gap-x-6">
              <router-link
                to="/login"
                class="rounded-md bg-primary-600 px-5 py-3 text-base font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
              >
                Get Started
              </router-link>
              <a href="#features" class="text-base font-medium text-primary-600 hover:text-primary-500">
                Learn more <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>
          <div class="mt-16 sm:mt-24 lg:col-span-6 lg:mt-0">
            <div class="bg-white shadow-xl rounded-2xl">
              <div class="relative h-80 overflow-hidden rounded-t-2xl">
                <div class="absolute inset-0 bg-gradient-to-br from-primary-400 to-primary-700 opacity-80"></div>
                <div class="absolute inset-0 flex items-center justify-center">
                  <div class="text-white space-y-4 p-6 text-center">
                    <img src="../assets/images/logo.png" alt="Tropical Vending Logo" class="h-24 w-auto mx-auto" />
                    <h2 class="text-xl font-semibold">Powered by AI</h2>
                    <p>Advanced analytics and predictions to optimize your business</p>
                  </div>
                </div>
              </div>
              <div class="p-6">
                <div class="space-y-4">
                  <div class="flex items-start">
                    <div class="flex-shrink-0">
                      <svg class="h-6 w-6 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <p class="ml-3 text-base text-gray-700">Manage multiple locations and machines</p>
                  </div>
                  <div class="flex items-start">
                    <div class="flex-shrink-0">
                      <svg class="h-6 w-6 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <p class="ml-3 text-base text-gray-700">Track product inventory and restocks</p>
                  </div>
                  <div class="flex items-start">
                    <div class="flex-shrink-0">
                      <svg class="h-6 w-6 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <p class="ml-3 text-base text-gray-700">Analyze sales trends and make data-driven decisions</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div id="features" class="py-24 bg-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            Streamline Your Vending Operations
          </h2>
          <p class="mx-auto mt-3 max-w-2xl text-xl text-gray-500 sm:mt-4">
            Everything you need to manage and grow your vending machine business
          </p>
        </div>

        <div class="mt-16">
          <div class="grid grid-cols-1 gap-12 lg:grid-cols-3">
            <!-- Feature 1 -->
            <div class="relative">
              <div class="absolute flex h-12 w-12 items-center justify-center rounded-md bg-primary-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div class="pl-16">
                <h3 class="text-xl font-medium text-gray-900">Location Management</h3>
                <p class="mt-2 text-base text-gray-500">
                  Organize machines by geographic locations. Track performance metrics by site to identify your most profitable locations.
                </p>
              </div>
            </div>

            <!-- Feature 2 -->
            <div class="relative">
              <div class="absolute flex h-12 w-12 items-center justify-center rounded-md bg-primary-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h12a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 10h16" />
                </svg>
              </div>
              <div class="pl-16">
                <h3 class="text-xl font-medium text-gray-900">Machine & Product Tracking</h3>
                <p class="mt-2 text-base text-gray-500">
                  Monitor each machine's inventory and restock needs. Manage product assortments and track performance by machine.
                </p>
              </div>
            </div>

            <!-- Feature 3 -->
            <div class="relative">
              <div class="absolute flex h-12 w-12 items-center justify-center rounded-md bg-primary-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div class="pl-16">
                <h3 class="text-xl font-medium text-gray-900">Smart Analytics</h3>
                <p class="mt-2 text-base text-gray-500">
                  Gain insights with AI-powered analytics. Track demand trends, predict inventory needs, and optimize machine placement.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div class="bg-primary-700">
      <div class="mx-auto max-w-7xl py-12 px-4 sm:px-6 lg:flex lg:items-center lg:justify-between lg:py-16 lg:px-8">
        <h2 class="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          <span class="block">Ready to optimize your vending operations?</span>
          <span class="block text-primary-200">Start using Tropical Vending today.</span>
        </h2>
        <div class="mt-8 flex lg:mt-0 lg:flex-shrink-0">
          <div class="inline-flex rounded-md shadow">
            <router-link
              to="/login"
              class="inline-flex items-center justify-center rounded-md border border-transparent bg-primary-600 px-5 py-3 text-base font-medium text-white hover:bg-primary-500"
            >
              Log In
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
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
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const router = useRouter();
const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
}
</script>

<style>
.bg-grid-primary-700\/20 {
  background-image: linear-gradient(to right, rgba(0, 69, 147, 0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 69, 147, 0.1) 1px, transparent 1px);
}
</style> 