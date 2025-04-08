<template>
  <div class="min-h-screen flex flex-col justify-between bg-gradient-to-b from-gray-50 to-gray-100 relative overflow-hidden">
    <!-- Background Pattern -->
    <div class="absolute inset-0 z-0 opacity-10">
      <div class="absolute inset-0 bg-grid-primary-700/20 bg-[size:20px_20px]"></div>
    </div>
    
    <!-- Login Content -->
    <div class="flex flex-col items-center justify-center flex-grow py-12 px-4 sm:px-6 lg:px-8 relative z-10">
      <!-- Login Card -->
      <div class="w-full max-w-xl space-y-6">
        <!-- Logo Section with Animation -->
        <div class="flex flex-col items-center animate-fade-in-down">
          <div class="bg-white rounded-full p-4 shadow-lg mb-6 transform transition-all duration-500 hover:shadow-xl hover:scale-105">
            <img src="../../assets/images/logo.png" class="h-24 w-auto" alt="Tropical Vending Logo" />
          </div>
        </div>
        
        <!-- Login Form Card -->
        <div class="bg-white p-8 sm:p-10 rounded-xl shadow-xl backdrop-blur-sm border border-gray-100 animate-fade-in-up">
          <h2 class="text-3xl font-bold text-gray-900 text-center mb-1">Welcome Back</h2>
          <p class="text-gray-600 text-center mb-8">Sign in to your account</p>
          
          <div v-if="error" class="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded mb-6 animate-shake" role="alert">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm">{{ error }}</p>
              </div>
            </div>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-6">
            <div class="space-y-5">
              <div class="group">
                <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <input
                    id="username"
                    v-model="username"
                    name="username"
                    type="text"
                    required
                    class="appearance-none block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 sm:text-sm"
                    placeholder="Enter your username"
                  />
                </div>
              </div>
              
              <div class="group">
                <label for="password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <input
                    id="password"
                    v-model="password"
                    name="password"
                    type="password"
                    required
                    class="appearance-none block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 sm:text-sm"
                    placeholder="Enter your password"
                  />
                </div>
              </div>
            </div>

            <div>
              <button
                type="submit"
                :disabled="loading"
                class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all duration-300 ease-in-out transform hover:translate-y-[-2px] disabled:opacity-50 disabled:hover:translate-y-0"
              >
                <span class="absolute left-0 inset-y-0 flex items-center pl-3">
                  <svg v-if="!loading" class="h-5 w-5 text-primary-400 group-hover:text-primary-300 transition-colors duration-200" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                  </svg>
                  <svg v-if="loading" class="animate-spin h-5 w-5 text-primary-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                {{ loading ? 'Signing in...' : 'Sign in' }}
              </button>
            </div>
          </form>
        </div>
        
        <div class="text-center mt-8 animate-fade-in">
          <p class="text-sm text-gray-600">Tropical Vending Management System</p>
        </div>
      </div>
    </div>
    
    <!-- Return to Home Link -->
    <div class="absolute top-4 left-4 z-20">
      <a href="/home" class="flex items-center text-primary-600 hover:text-primary-700 transition-colors duration-300">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
        </svg>
        <span class="text-sm font-medium">Return to Home</span>
      </a>
    </div>
    
    <!-- Footer -->
    <div class="relative z-10">
      <AppFooter />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import AppFooter from '../../components/AppFooter.vue'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  
  try {
    const result = await authStore.login(username.value, password.value)
    
    if (result.success) {
      router.push('/dashboard')
    } else {
      error.value = result.message || 'Login failed'
    }
  } catch (err) {
    error.value = 'An error occurred during login'
    console.error('Login error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Focus username input on page load
  document.getElementById('username').focus()
})
</script>

<style scoped>
.bg-grid-primary-700\/20 {
  background-image: linear-gradient(to right, rgba(0, 69, 147, 0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 69, 147, 0.1) 1px, transparent 1px);
}

/* Animation classes */
.animate-fade-in-down {
  animation: fade-in-down 0.7s ease-out forwards;
}

.animate-fade-in-up {
  animation: fade-in-up 0.7s ease-out forwards;
  animation-delay: 0.2s;
  opacity: 0;
}

.animate-fade-in {
  animation: fade-in 0.7s ease-out forwards;
  animation-delay: 0.4s;
  opacity: 0;
}

.animate-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes fade-in-down {
  0% {
    opacity: 0;
    transform: translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in-up {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

@keyframes shake {
  10%, 90% {
    transform: translateX(-1px);
  }
  20%, 80% {
    transform: translateX(2px);
  }
  30%, 50%, 70% {
    transform: translateX(-4px);
  }
  40%, 60% {
    transform: translateX(4px);
  }
}
</style> 