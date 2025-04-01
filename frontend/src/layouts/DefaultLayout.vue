<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-primary-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <router-link to="/" class="flex items-center">
                <img src="../assets/images/logo.png" alt="Tropical Vending Logo" class="h-8 w-auto mr-2" />
                <span class="text-white text-xl font-bold">Tropical Vending</span>
              </router-link>
            </div>
            <div class="hidden md:block">
              <div class="ml-10 flex items-baseline space-x-4">
                <router-link 
                  v-for="item in navigation" 
                  :key="item.name" 
                  :to="item.href" 
                  :class="[
                    $route.name === item.routeName
                      ? 'bg-primary-800 text-white'
                      : 'text-white hover:bg-primary-600',
                    'px-3 py-2 rounded-md text-sm font-medium'
                  ]"
                >
                  {{ item.name }}
                </router-link>
              </div>
            </div>
          </div>
          <div class="hidden md:block">
            <div class="ml-4 flex items-center md:ml-6">
              <div class="ml-3 relative">
                <div class="flex items-center">
                  <span class="text-white mr-2">{{ userName }}</span>
                  <button
                    @click="logout"
                    class="bg-primary-800 p-1 rounded-full text-white hover:bg-primary-600 focus:outline-none"
                  >
                    <span class="sr-only">Logout</span>
                    <span class="text-sm">Logout</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="-mr-2 flex md:hidden">
            <!-- Mobile menu button -->
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-primary-600 focus:outline-none"
            >
              <span class="sr-only">Open main menu</span>
              <svg
                class="h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile menu, show/hide based on menu state. -->
      <div class="md:hidden" v-show="mobileMenuOpen">
        <div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            :class="[
              $route.name === item.routeName
                ? 'bg-primary-800 text-white'
                : 'text-white hover:bg-primary-600',
              'block px-3 py-2 rounded-md text-base font-medium'
            ]"
            @click="mobileMenuOpen = false"
          >
            {{ item.name }}
          </router-link>
        </div>
        <div class="pt-4 pb-3 border-t border-primary-600">
          <div class="flex items-center px-5">
            <div class="flex-shrink-0">
              <span class="text-white text-xl">{{ userName.charAt(0) }}</span>
            </div>
            <div class="ml-3">
              <div class="text-base font-medium text-white">{{ userName }}</div>
            </div>
          </div>
          <div class="mt-3 px-2 space-y-1">
            <button
              @click="logout"
              class="block px-3 py-2 rounded-md text-base font-medium text-white hover:bg-primary-600 w-full text-left"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="px-4 py-4 sm:px-0">
          <router-view />
        </div>
      </div>
    </main>

    <footer class="bg-white py-4 border-t border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col items-center">
          <img src="../assets/images/logo.png" alt="Tropical Vending Logo" class="h-8 w-auto mb-2" />
          <p class="text-center text-gray-600 font-medium mb-1">
            © {{ new Date().getFullYear() }} Tropical Vending
          </p>
          <p class="text-center text-gray-500 text-sm">
            Made with <span class="text-yellow-500">💛</span> by <a href="https://garat.dev" target="_blank" class="text-primary-600 hover:text-primary-700">Garat.dev</a>
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const authStore = useAuthStore()

const mobileMenuOpen = ref(false)

const navigation = [
  { name: 'Dashboard', href: '/', routeName: 'dashboard' },
  { name: 'Locations', href: '/locations', routeName: 'locations' },
  { name: 'Machines', href: '/machines', routeName: 'machines' },
  { name: 'Products', href: '/products', routeName: 'products' },
  { name: 'Visits', href: '/restocks', routeName: 'restocks' },
  { name: 'Purchases', href: '/purchases', routeName: 'purchases' },
  { name: 'Analytics', href: '/analytics', routeName: 'analytics' },
]

const userName = computed(() => {
  if (!authStore.user) return 'User'
  if (authStore.user.first_name || authStore.user.last_name) {
    return `${authStore.user.first_name} ${authStore.user.last_name}`.trim()
  }
  return authStore.user.username
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}

// Fetch user data if needed
if (authStore.isAuthenticated && !authStore.user) {
  authStore.fetchUser()
}
</script> 