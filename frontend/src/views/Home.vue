<template>
  <div class="bg-gradient-to-b from-gray-50 to-gray-100 min-h-screen">
    <!-- Navigation -->
    <div class="sticky top-0 bg-white/95 shadow-sm z-50 backdrop-blur-sm transition-all duration-300">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex h-20 items-center justify-between">
          <div class="flex items-center">
            <div class="text-primary-700 text-2xl font-bold flex items-center">
              <img src="../assets/images/logo.png" alt="Tropical Vending Logo" class="h-10 w-auto mr-2" />
              Tropical Vending
            </div>
          </div>
          <div class="flex items-center space-x-6">
            <!-- Navigation Links -->
            <div class="hidden md:flex space-x-6 mr-4">
              <a href="#home" class="text-gray-600 hover:text-primary-600 font-medium transition-colors duration-300">Home</a>
              <a href="#what-we-do" class="text-gray-600 hover:text-primary-600 font-medium transition-colors duration-300">What do we Do?</a>
              <a href="#about" class="text-gray-600 hover:text-primary-600 font-medium transition-colors duration-300">About</a>
              <a href="#contact" class="text-gray-600 hover:text-primary-600 font-medium transition-colors duration-300">Contact</a>
            </div>
            
            <template v-if="isAuthenticated">
              <router-link
                to="/"
                class="text-primary-600 hover:text-primary-700 font-medium transition-colors duration-300"
              >
                Dashboard
              </router-link>
              <button
                @click="handleLogout"
                class="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-300"
              >
                Logout
              </button>
            </template>
            <template v-else>
              <router-link
                to="/login"
                class="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-all duration-300"
              >
                Login
              </router-link>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Hero Section -->
    <div id="home" class="relative overflow-hidden">
      <!-- Hero Background Image -->
      <div class="absolute inset-0 z-0">
        <div class="absolute inset-0 bg-gradient-to-r from-primary-900/90 to-primary-700/80"></div>
        <img src="/vending-night.jpg" alt="Vending Machine at Night" class="w-full h-full object-cover" />
      </div>
      
      <!-- Hero Content -->
      <div class="relative z-10 mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8 pt-36">
        <div class="lg:grid lg:grid-cols-12 lg:gap-8">
          <div class="lg:col-span-6 animate-fade-in-up">
            <h1 class="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-6xl">
              <span class="block">Your Local</span>
              <span class="block text-primary-200">Vending Partner</span>
            </h1>
            <p class="mt-6 text-lg text-gray-100">
              Tropical Vending is a locally owned and operated vending company serving the Broward and Dade area. We're big enough to handle any vending situation yet small enough to offer personalized service.
            </p>
            <div class="mt-8 flex flex-wrap gap-4">
              <div class="flex items-center bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
                <svg class="h-6 w-6 text-primary-200 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <p class="ml-2 text-white">Vending Machines provided Free</p>
              </div>
              <div class="flex items-center bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
                <svg class="h-6 w-6 text-primary-200 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <p class="ml-2 text-white">No charge for maintenance</p>
              </div>
              <div class="flex items-center bg-white/10 backdrop-blur-sm rounded-lg px-3 py-2">
                <svg class="h-6 w-6 text-primary-200 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <p class="ml-2 text-white">24/7 Customer Service</p>
              </div>
            </div>
            <div class="mt-10 flex items-center gap-x-6">
              <a href="#what-we-do" class="rounded-md bg-white px-5 py-3 text-base font-medium text-primary-700 shadow-sm hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-700 transition-all duration-300 hover:translate-y-[-2px]">
                Learn More
              </a>
              <a href="#contact" class="text-base font-medium text-white hover:text-primary-200 transition-all duration-300 hover:translate-x-2">
                Contact Us <span aria-hidden="true">→</span>
              </a>
            </div>
          </div>
          <div class="mt-16 sm:mt-24 lg:col-span-6 lg:mt-0 animate-fade-in-right">
            <div class="bg-white/10 backdrop-blur-sm rounded-2xl shadow-xl transform transition-all duration-500 hover:shadow-2xl hover:scale-[1.02] overflow-hidden">
              <div class="p-6">
                <div class="space-y-4">
                  <div class="flex items-start">
                    <div class="flex-shrink-0">
                      <svg class="h-6 w-6 text-primary-200" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <p class="ml-3 text-base text-white">Daily or weekly restocking of machines</p>
                  </div>
                  <div class="flex items-start">
                    <div class="flex-shrink-0">
                      <svg class="h-6 w-6 text-primary-200" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <p class="ml-3 text-base text-white">Friendly courteous route drivers</p>
                  </div>
                  <div class="flex items-start">
                    <div class="flex-shrink-0">
                      <svg class="h-6 w-6 text-primary-200" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <p class="ml-3 text-base text-white">Quality products your employees desire</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- What do we Do? Section -->
    <div id="what-we-do" class="py-24 bg-white scroll-mt-20">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl animate-fade-in">
            What do we Do?
          </h2>
          <p class="mx-auto mt-3 max-w-2xl text-xl text-gray-500 sm:mt-4">
            Providing exceptional vending services throughout South Florida
          </p>
        </div>

        <div class="mt-16">
          <div class="grid grid-cols-1 gap-12 lg:grid-cols-3">
            <!-- Feature 1 with image -->
            <div class="relative transform transition-all duration-500 hover:translate-y-[-8px] animate-fade-in-up" style="animation-delay: 100ms;">
              <div class="overflow-hidden rounded-lg mb-6 shadow-lg">
                <img src="/warehouse.jpg" alt="Warehouse Vending" class="w-full h-48 object-cover object-center" />
              </div>
              <div class="absolute top-2 left-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary-500 text-white shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 class="text-xl font-medium text-gray-900">Strategic Placement</h3>
              <p class="mt-2 text-base text-gray-500">
                We place vending machines in warehouses, residential areas, and businesses throughout Broward and Dade counties. Each location is strategically selected for optimal convenience.
              </p>
            </div>

            <!-- Feature 2 with image -->
            <div class="relative transform transition-all duration-500 hover:translate-y-[-8px] animate-fade-in-up" style="animation-delay: 200ms;">
              <div class="overflow-hidden rounded-lg mb-6 shadow-lg">
                <img src="/snacks.jpg" alt="Snack Selection" class="w-full h-48 object-cover object-center" />
              </div>
              <div class="absolute top-2 left-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary-500 text-white shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h12a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 10h16" />
                </svg>
              </div>
              <h3 class="text-xl font-medium text-gray-900">Maintenance & Restocking</h3>
              <p class="mt-2 text-base text-gray-500">
                We provide free vending machines with no maintenance costs. Our friendly route drivers ensure machines are regularly restocked and kept clean and functioning properly.
              </p>
            </div>

            <!-- Feature 3 with image -->
            <div class="relative transform transition-all duration-500 hover:translate-y-[-8px] animate-fade-in-up" style="animation-delay: 300ms;">
              <div class="overflow-hidden rounded-lg mb-6 shadow-lg">
                <img src="/customer.jpg" alt="Customer Service" class="w-full h-48 object-cover object-center" />
              </div>
              <div class="absolute top-2 left-2 flex h-12 w-12 items-center justify-center rounded-full bg-primary-500 text-white shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 class="text-xl font-medium text-gray-900">Customer Service</h3>
              <p class="mt-2 text-base text-gray-500">
                We provide 24/7 customer service and establish friendly professional relationships with our clients. We're committed to keeping your vending machines full, clean, and in proper working order.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- About Section with Image -->
    <div id="about" class="py-24 bg-gray-50 scroll-mt-20 overflow-hidden">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl animate-fade-in">
            About Tropical Vending
          </h2>
          <p class="mx-auto mt-3 max-w-2xl text-xl text-gray-500 sm:mt-4">
            Locally owned and operated in South Florida
          </p>
        </div>
        
        <div class="mt-16 lg:grid lg:grid-cols-2 lg:gap-16 items-center">
          <div class="animate-fade-in-left mb-12 lg:mb-0">
            <div class="rounded-2xl overflow-hidden shadow-xl">
              <img src="/cokes.jpg" alt="Coca-Cola Vending" class="w-full h-auto transform transition-transform duration-700 hover:scale-105" />
            </div>
          </div>
          <div class="mx-auto animate-fade-in-right">
            <p class="text-lg text-gray-600 mb-6">
              Tropical Vending is a locally owned and operated vending company serving businesses throughout the Broward and Dade areas. We're proud to be a part of the South Florida community.
            </p>
            <p class="text-lg text-gray-600 mb-6">
              Our approach is simple: we're big enough to handle any vending situation yet small enough to offer personalized service. This balance allows us to provide the attention to detail and custom solutions that large national companies often can't match.
            </p>
            <p class="text-lg text-gray-600">
              We understand that quality refreshments and snacks are important to employee satisfaction and productivity. That's why we work closely with each client to provide the quality products your employees desire, while maintaining friendly, professional service at all times.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Section with Map Background -->
    <div id="contact" class="py-24 bg-white scroll-mt-20 relative">
      <!-- Background effect -->
      <div class="absolute inset-0 z-0 opacity-10">
        <div class="absolute inset-0 bg-primary-700 opacity-10"></div>
      </div>
      
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="text-center">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl animate-fade-in">
            Get In Touch
          </h2>
          <p class="mx-auto mt-3 max-w-2xl text-xl text-gray-500 sm:mt-4">
            Ready to improve your vending services? Contact us today.
          </p>
        </div>
        
        <div class="mt-12 mx-auto max-w-5xl">
          <div class="flex flex-col rounded-2xl bg-white shadow-lg transform transition-all duration-500 hover:shadow-xl animate-fade-in-left">
            <div class="flex-1 p-10">
              <h3 class="text-xl font-medium text-gray-900">Office Location</h3>
              <address class="mt-4 not-italic text-base text-gray-500">
                <p class="mt-2">4749 NW 109th Court</p>
                <p>Doral, FL 33178</p>
                <p class="mt-4 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <a href="tel:3057739307" class="text-primary-600 hover:text-primary-500">305-773-9307</a>
                </p>
                <p class="mt-2 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <a href="mailto:ivan.munoz@tropicalvend.com" class="text-primary-600 hover:text-primary-500">ivan.munoz@tropicalvend.com</a>
                </p>
                <p class="mt-4 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>24/7 Customer Service</span>
                </p>
              </address>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-white py-8 border-t border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="text-center md:text-left mb-4 md:mb-0">
            <div class="text-primary-700 text-xl font-bold flex items-center justify-center md:justify-start">
              <img src="../assets/images/logo.png" alt="Tropical Vending Logo" class="h-8 w-auto mr-2" />
              Tropical Vending
            </div>
            <p class="text-sm text-gray-500 mt-2">
              Serving Broward & Dade Counties
            </p>
          </div>
          
          <div class="flex space-x-6">
            <a href="#home" class="text-gray-500 hover:text-primary-600 transition-colors duration-300">Home</a>
            <a href="#what-we-do" class="text-gray-500 hover:text-primary-600 transition-colors duration-300">What do we Do?</a>
            <a href="#about" class="text-gray-500 hover:text-primary-600 transition-colors duration-300">About</a>
            <a href="#contact" class="text-gray-500 hover:text-primary-600 transition-colors duration-300">Contact</a>
          </div>
        </div>
        
        <div class="mt-8 pt-6 border-t border-gray-200">
          <p class="text-center text-gray-500 text-sm mb-2">
            &copy; 2025 Tropical Vending. All rights reserved.
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
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/auth';

const router = useRouter();
const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);

const handleLogout = () => {
  const redirectPath = authStore.logout();
  router.push(redirectPath);
};

onMounted(() => {
  // Add smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 80, // Offset for fixed header
          behavior: 'smooth'
        });
      }
    });
  });

  // Animate elements when they come into view
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1
  });

  document.querySelectorAll('.animate-fade-in, .animate-fade-in-up, .animate-fade-in-left, .animate-fade-in-right').forEach(element => {
    observer.observe(element);
  });
});
</script>

<style>
.bg-grid-primary-700\/20 {
  background-image: linear-gradient(to right, rgba(0, 69, 147, 0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 69, 147, 0.1) 1px, transparent 1px);
}

.scroll-mt-20 {
  scroll-margin-top: 5rem;
}

/* Animation classes */
.animate-fade-in {
  opacity: 0;
  transition: opacity 1s ease-out;
}

.animate-fade-in-up {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}

.animate-fade-in-left {
  opacity: 0;
  transform: translateX(-20px);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}

.animate-fade-in-right {
  opacity: 0;
  transform: translateX(20px);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}

/* Visible state for animations */
.is-visible {
  opacity: 1;
  transform: translate(0, 0);
}

/* Add backdrop-blur support for Firefox */
@supports (-moz-appearance: none) {
  .backdrop-blur-sm {
    background-color: rgba(255, 255, 255, 0.95);
  }
}
</style> 