<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
    <!-- Animated Background Elements -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-blue-500/30 to-cyan-500/30 rounded-full blur-3xl animate-pulse" style="animation-delay: 2s;"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse" style="animation-delay: 4s;"></div>
    </div>

    <!-- Return to Home Link -->
    <div class="absolute top-6 left-6 z-20">
      <a href="/home" class="return-home-link group">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 transition-transform group-hover:-translate-x-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
        </svg>
        <span class="font-medium">Return to Home</span>
      </a>
    </div>
    
    <!-- Login Content -->
    <div class="flex flex-col items-center justify-center min-h-screen py-12 px-4 sm:px-6 lg:px-8 relative z-10">
      <div class="w-full max-w-md space-y-8">
        <!-- Logo Section with Animation -->
        <div class="text-center animate-fade-in-down">
          <div class="relative inline-block">
            <div class="absolute inset-0 bg-gradient-to-r from-purple-500/30 to-pink-500/30 rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div class="relative bg-white/10 backdrop-blur-xl border border-white/20 rounded-full p-6 shadow-2xl transform transition-all duration-500 hover:scale-110 hover:shadow-purple-500/25 group">
              <img src="../../assets/images/logo.png" class="h-20 w-auto" alt="Tropical Vending Logo" />
            </div>
          </div>
          <h1 class="mt-6 text-4xl font-bold bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent">
            Welcome Back
          </h1>
          <p class="mt-2 text-lg text-gray-400">
            Sign in to your account
          </p>
        </div>
        
        <!-- Login Form Card -->
        <div class="glass-card p-8 space-y-6 animate-fade-in-up">
          <!-- Error Alert -->
          <div v-if="error" class="error-alert animate-shake" role="alert">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-300">{{ error }}</p>
              </div>
            </div>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-6">
            <!-- Username Field -->
            <div class="form-group">
              <label for="username" class="form-label">Username</label>
              <div class="relative">
                <div class="input-icon">
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
                  class="form-input"
                  placeholder="Enter your username"
                />
              </div>
            </div>
            
            <!-- Password Field -->
            <div class="form-group">
              <label for="password" class="form-label">Password</label>
              <div class="relative">
                <div class="input-icon">
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
                  class="form-input"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <!-- Submit Button -->
            <div>
              <button
                type="submit"
                :disabled="loading"
                class="login-button group"
              >
                <span class="absolute left-0 inset-y-0 flex items-center pl-4">
                  <svg v-if="!loading" class="h-5 w-5 text-white/80 group-hover:text-white transition-colors duration-200" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                  </svg>
                  <svg v-if="loading" class="animate-spin h-5 w-5 text-white/80" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                {{ loading ? 'Signing in...' : 'Sign in' }}
              </button>
            </div>
          </form>
        </div>
        
        <!-- Footer Text -->
        <div class="text-center animate-fade-in">
          <p class="text-sm text-gray-400">
            Tropical Vending Management System
          </p>
          <p class="text-xs text-gray-500 mt-2">
            Secure access to your vending operations
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import '../../assets/css/login.css'

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

 