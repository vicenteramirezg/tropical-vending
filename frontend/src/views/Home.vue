<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
    <!-- Animated Background Elements -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-blue-500/30 to-cyan-500/30 rounded-full blur-3xl animate-pulse" style="animation-delay: 2s;"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse" style="animation-delay: 4s;"></div>
    </div>

    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-white/10 border-b border-white/20 transition-all duration-500">
      <div class="max-w-7xl mx-auto px-6 sm:px-8">
        <div class="flex items-center justify-between h-20">
          <!-- Logo -->
          <div class="flex items-center space-x-3 group">
            <div class="relative">
              <img src="../assets/images/logo.png" alt="Tropical Vending" class="h-10 w-auto transition-transform duration-300 group-hover:scale-110" />
              <div class="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </div>
            <span class="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              Tropical Vending
            </span>
          </div>

            <!-- Navigation Links -->
          <div class="hidden md:flex items-center space-x-8">
            <a href="#home" class="nav-link">Home</a>
            <a href="#services" class="nav-link">Services</a>
            <a href="#about" class="nav-link">About</a>
            <a href="#contact" class="nav-link">Contact</a>
            </div>
            
          <!-- Auth Buttons -->
          <div class="flex items-center space-x-4">
            <template v-if="isAuthenticated">
              <router-link
                to="/dashboard"
                class="btn-secondary"
              >
                Dashboard
              </router-link>
              <button
                @click="handleLogout"
                class="btn-primary"
              >
                Logout
              </button>
            </template>
            <template v-else>
              <router-link
                to="/login"
                class="btn-primary"
              >
                Login
              </router-link>
            </template>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section id="home" class="relative min-h-screen flex items-center justify-center px-6 sm:px-8">
      <div class="max-w-7xl mx-auto w-full">
        <div class="grid lg:grid-cols-2 gap-16 items-center">
          <!-- Hero Content -->
          <div class="text-center lg:text-left animate-fade-in-up">
            <div class="mb-6">
              <span class="inline-block px-4 py-2 rounded-full bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 text-purple-200 text-sm font-medium mb-4 backdrop-blur-sm">
                ✨ South Florida's Premier Vending Partner
              </span>
      </div>
      
            <h1 class="text-5xl lg:text-7xl font-bold mb-8 leading-tight">
              <span class="block bg-gradient-to-r from-white via-gray-100 to-gray-300 bg-clip-text text-transparent">
                Your Local
              </span>
              <span class="block bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent animate-gradient">
                Vending Partner
              </span>
            </h1>
            
            <p class="text-xl text-gray-300 mb-10 max-w-2xl mx-auto lg:mx-0 leading-relaxed">
              Tropical Vending delivers exceptional vending services throughout Broward and Dade counties. 
              We're big enough to handle any situation, yet small enough for personalized service.
            </p>

            <!-- Feature Pills -->
            <div class="flex flex-wrap gap-4 mb-12 justify-center lg:justify-start">
              <div class="feature-pill">
                <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Free Vending Machines
              </div>
              <div class="feature-pill">
                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                No Maintenance Costs
              </div>
              <div class="feature-pill">
                <svg class="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                24/7 Customer Service
              </div>
            </div>

            <!-- CTA Buttons -->
            <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <a href="#services" class="btn-primary-large group">
                Discover Our Services
                <svg class="w-5 h-5 ml-2 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path>
                </svg>
              </a>
              <a href="#contact" class="btn-secondary-large group">
                Get In Touch
                <svg class="w-5 h-5 ml-2 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </a>
            </div>
          </div>

          <!-- Hero Visual -->
          <div class="relative animate-fade-in-right">
            <div class="glass-card p-8 transform hover:scale-105 transition-all duration-700">
              <div class="space-y-6">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                      </svg>
                    </div>
                  <div>
                    <h3 class="text-white font-semibold">Daily Restocking</h3>
                    <p class="text-gray-400 text-sm">Fresh products delivered regularly</p>
                  </div>
                </div>
                
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 rounded-full bg-gradient-to-r from-blue-400 to-cyan-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                      </svg>
                    </div>
                  <div>
                    <h3 class="text-white font-semibold">Friendly Service</h3>
                    <p class="text-gray-400 text-sm">Courteous professional drivers</p>
                  </div>
                </div>
                
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 rounded-full bg-gradient-to-r from-purple-400 to-pink-500 flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                      </svg>
                    </div>
                  <div>
                    <h3 class="text-white font-semibold">Quality Products</h3>
                    <p class="text-gray-400 text-sm">Premium snacks and beverages</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Services Section -->
    <section id="services" class="py-32 relative">
      <div class="max-w-7xl mx-auto px-6 sm:px-8">
        <!-- Section Header -->
        <div class="text-center mb-20 animate-fade-in">
          <span class="inline-block px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 text-blue-200 text-sm font-medium mb-4 backdrop-blur-sm">
            🚀 Our Services
          </span>
          <h2 class="text-4xl lg:text-6xl font-bold mb-6 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
            What We Do
          </h2>
          <p class="text-xl text-gray-400 max-w-3xl mx-auto">
            Providing exceptional vending services throughout South Florida with cutting-edge technology and personalized care
          </p>
        </div>

        <!-- Services Grid -->
        <div class="grid md:grid-cols-3 gap-8">
          <div class="service-card group" style="animation-delay: 100ms;">
            <div class="service-image-container">
              <img src="/warehouse.jpg" alt="Strategic Placement" class="service-image" />
              <div class="service-overlay">
                <div class="service-icon bg-gradient-to-r from-purple-500 to-pink-500">
                  <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                </div>
              </div>
              </div>
            <div class="p-8">
              <h3 class="text-2xl font-bold text-white mb-4">Strategic Placement</h3>
              <p class="text-gray-400 leading-relaxed">
                We strategically place vending machines in high-traffic locations across Broward and Dade counties, 
                ensuring maximum convenience for your customers and employees.
              </p>
            </div>
              </div>

          <div class="service-card group" style="animation-delay: 200ms;">
            <div class="service-image-container">
              <img src="/snacks.jpg" alt="Maintenance & Restocking" class="service-image" />
              <div class="service-overlay">
                <div class="service-icon bg-gradient-to-r from-blue-500 to-cyan-500">
                  <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                </div>
              </div>
            </div>
            <div class="p-8">
              <h3 class="text-2xl font-bold text-white mb-4">Maintenance & Restocking</h3>
              <p class="text-gray-400 leading-relaxed">
                Comprehensive maintenance and regular restocking services ensure your machines are always operational 
                and fully stocked with fresh, quality products.
              </p>
            </div>
              </div>

          <div class="service-card group" style="animation-delay: 300ms;">
            <div class="service-image-container">
              <img src="/customer.jpg" alt="Customer Service" class="service-image" />
              <div class="service-overlay">
                <div class="service-icon bg-gradient-to-r from-green-500 to-emerald-500">
                  <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"></path>
                </svg>
                </div>
              </div>
            </div>
            <div class="p-8">
              <h3 class="text-2xl font-bold text-white mb-4">24/7 Support</h3>
              <p class="text-gray-400 leading-relaxed">
                Round-the-clock customer service ensures immediate response to any issues, 
                maintaining the highest level of service reliability for your business.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-32 relative">
      <div class="max-w-7xl mx-auto px-6 sm:px-8">
        <div class="grid lg:grid-cols-2 gap-16 items-center">
          <!-- About Image -->
          <div class="relative animate-fade-in-left">
            <div class="glass-card p-4 transform hover:scale-105 transition-all duration-700">
              <img src="/cokes.jpg" alt="About Tropical Vending" class="rounded-2xl w-full h-auto" />
            </div>
            <div class="absolute -bottom-6 -right-6 w-32 h-32 bg-gradient-to-r from-purple-500/30 to-pink-500/30 rounded-full blur-2xl"></div>
    </div>

          <!-- About Content -->
          <div class="animate-fade-in-right">
            <span class="inline-block px-4 py-2 rounded-full bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 text-green-200 text-sm font-medium mb-6 backdrop-blur-sm">
              🌴 About Us
            </span>
            
            <h2 class="text-4xl lg:text-5xl font-bold mb-8 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              Locally Owned & Operated
          </h2>
            
            <div class="space-y-6 text-lg text-gray-300 leading-relaxed">
              <p>
                Tropical Vending is a locally owned and operated vending company proudly serving businesses 
                throughout the Broward and Dade areas. We're deeply rooted in the South Florida community.
              </p>
              
              <p>
                Our unique approach combines the capabilities of a large operation with the personalized 
                attention of a local business. This balance allows us to deliver custom solutions and 
                exceptional service that national companies simply can't match.
              </p>
              
              <p>
                We understand that quality refreshments directly impact employee satisfaction and productivity. 
                That's why we work closely with each client to provide exactly what your team needs, 
                while maintaining the highest standards of professional service.
          </p>
        </div>
        
            <!-- Stats -->
            <div class="grid grid-cols-2 gap-8 mt-12">
              <div class="text-center">
                <div class="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">24/7</div>
                <div class="text-gray-400">Customer Support</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mb-2">100%</div>
                <div class="text-gray-400">Local Owned</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-32 relative">
      <div class="max-w-7xl mx-auto px-6 sm:px-8">
        <!-- Section Header -->
        <div class="text-center mb-20 animate-fade-in">
          <span class="inline-block px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 text-cyan-200 text-sm font-medium mb-4 backdrop-blur-sm">
            📞 Get In Touch
          </span>
          <h2 class="text-4xl lg:text-6xl font-bold mb-6 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
            Contact Us
          </h2>
          <p class="text-xl text-gray-400 max-w-3xl mx-auto">
            Ready to enhance your vending services? Let's start a conversation today.
          </p>
        </div>
        
        <div class="grid lg:grid-cols-2 gap-12">
          <!-- Contact Info -->
          <div class="glass-card p-10 animate-fade-in-left">
            <h3 class="text-2xl font-bold text-white mb-8">Office Location</h3>
            
            <div class="space-y-6">
              <div class="contact-item">
                <div class="contact-icon bg-gradient-to-r from-purple-500 to-pink-500">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="text-white font-semibold mb-1">Address</h4>
                  <p class="text-gray-400">4749 NW 109th Court<br>Doral, FL 33178</p>
                </div>
              </div>

              <div class="contact-item">
                <div class="contact-icon bg-gradient-to-r from-blue-500 to-cyan-500">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                    </svg>
                </div>
                <div>
                  <h4 class="text-white font-semibold mb-1">Phone</h4>
                  <a href="tel:3057739307" class="text-cyan-400 hover:text-cyan-300 transition-colors">305-773-9307</a>
                </div>
              </div>

              <div class="contact-item">
                <div class="contact-icon bg-gradient-to-r from-green-500 to-emerald-500">
                  <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                    </svg>
                </div>
                <div>
                  <h4 class="text-white font-semibold mb-1">WhatsApp</h4>
                  <a href="https://wa.me/13057739307?text=Hello%20Tropical%20Vending,%20I%20would%20like%20to%20do%20business%20with%20you." 
                     target="_blank" 
                     rel="noopener noreferrer" 
                     class="text-green-400 hover:text-green-300 transition-colors">
                    Chat with us
                  </a>
                </div>
              </div>

              <div class="contact-item">
                <div class="contact-icon bg-gradient-to-r from-orange-500 to-red-500">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                </div>
                <div>
                  <h4 class="text-white font-semibold mb-1">Email</h4>
                  <a href="mailto:ivan.munoz@tropicalvend.com" class="text-orange-400 hover:text-orange-300 transition-colors">ivan.munoz@tropicalvend.com</a>
                </div>
              </div>
              </div>
            </div>
            
          <!-- Map -->
          <div class="glass-card p-4 animate-fade-in-right">
            <div class="rounded-2xl overflow-hidden h-96 lg:h-full">
              <iframe 
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3592.2069490866943!2d-80.3835361!3d25.8168505!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x88d9bb0a8d6a7a45%3A0x4c435a70c1f01e69!2s4749%20NW%20109th%20Ct%2C%20Doral%2C%20FL%2033178!5e0!3m2!1sen!2sus!4v1721341650780!5m2!1sen!2sus" 
                width="100%" 
                height="100%" 
                style="border:0;" 
                allowfullscreen="" 
                loading="lazy" 
                referrerpolicy="no-referrer-when-downgrade"
                title="Tropical Vending Office Location"
                class="w-full h-full filter grayscale hover:grayscale-0 transition-all duration-500">
              </iframe>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="py-12 border-t border-white/10 backdrop-blur-sm">
      <div class="max-w-7xl mx-auto px-6 sm:px-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="flex items-center space-x-3 mb-6 md:mb-0">
            <img src="../assets/images/logo.png" alt="Tropical Vending" class="h-8 w-auto" />
            <span class="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
              Tropical Vending
            </span>
          </div>
          
          <div class="flex space-x-8">
            <a href="#home" class="footer-link">Home</a>
            <a href="#services" class="footer-link">Services</a>
            <a href="#about" class="footer-link">About</a>
            <a href="#contact" class="footer-link">Contact</a>
          </div>
        </div>
        
        <div class="mt-8 pt-8 border-t border-white/10 text-center">
          <p class="text-gray-400 mb-2">
            &copy; 2025 Tropical Vending. All rights reserved.
          </p>
          <p class="text-gray-500">
            Made with <span class="text-yellow-400">💛</span> by 
            <a href="https://garat.dev" target="_blank" class="text-purple-400 hover:text-purple-300 transition-colors">Garat.dev</a>
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
import '../assets/css/home.css';

const router = useRouter();
const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);

const handleLogout = () => {
  const redirectPath = authStore.logout();
  router.push(redirectPath);
};

onMounted(() => {
  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        const headerOffset = 80;
        const elementPosition = targetElement.offsetTop;
        const offsetPosition = elementPosition - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // Intersection Observer for animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Observe all animated elements
  document.querySelectorAll('.animate-fade-in, .animate-fade-in-up, .animate-fade-in-left, .animate-fade-in-right, .service-card').forEach(element => {
    observer.observe(element);
  });

  // Parallax effect for background elements
  const handleScroll = () => {
    const scrolled = window.pageYOffset;
    const parallaxElements = document.querySelectorAll('.absolute');
    
    parallaxElements.forEach((element, index) => {
      const speed = 0.5 + (index * 0.1);
      const yPos = -(scrolled * speed);
      element.style.transform = `translateY(${yPos}px)`;
    });
  };

  window.addEventListener('scroll', handleScroll);

  // Cleanup
  return () => {
    window.removeEventListener('scroll', handleScroll);
  };
});
</script>

 