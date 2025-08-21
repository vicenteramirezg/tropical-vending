<template>
  <div class="mt-1 flex rounded-md shadow-sm relative">
    <!-- Desktop/Tablet: Show stepper buttons -->
    <button 
      v-if="showSteppers"
      type="button"
      @click="decrement"
      class="hidden sm:inline-flex relative items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      :disabled="disabled"
    >
      <span class="sr-only">Decrease {{ label || 'value' }}</span>
      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path>
      </svg>
    </button>
    
    <!-- Number Input -->
    <input 
      :id="inputId"
      type="number" 
      :value="modelValue"
      @input="updateValue"
      @focus="handleFocus"
      @blur="handleBlur"
      :min="min"
      :max="max"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="inputClasses"
      inputmode="numeric"
      pattern="[0-9]*"
    >
    
    <!-- Desktop/Tablet: Show stepper buttons -->
    <button 
      v-if="showSteppers"
      type="button"
      @click="increment"
      class="hidden sm:inline-flex relative items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
      :disabled="disabled"
    >
      <span class="sr-only">Increase {{ label || 'value' }}</span>
      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  min: {
    type: [String, Number],
    default: 0
  },
  max: {
    type: [String, Number],
    default: null
  },
  placeholder: {
    type: String,
    default: '0'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    default: ''
  },
  inputId: {
    type: String,
    default: ''
  },
  showSteppers: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur'])

const isFocused = ref(false)

// Computed classes for the input field
const inputClasses = computed(() => {
  const baseClasses = 'focus:ring-primary-500 focus:border-primary-500 block w-full text-center sm:text-sm number-input-mobile'
  
  if (props.showSteppers) {
    // Desktop/Tablet with steppers: no rounded corners on sides
    return `${baseClasses} border-gray-300 rounded-none sm:border-l-0 sm:border-r-0 sm:rounded-none rounded-md`
  } else {
    // Mobile without steppers or always without steppers: full rounded
    return `${baseClasses} border-gray-300 rounded-md`
  }
})

const updateValue = (event) => {
  const value = event.target.value
  emit('update:modelValue', value)
}

const increment = () => {
  if (props.disabled) return
  
  const currentValue = props.modelValue === '' ? 0 : parseInt(props.modelValue) || 0
  const newValue = props.max !== null ? Math.min(currentValue + 1, parseInt(props.max)) : currentValue + 1
  emit('update:modelValue', newValue)
}

const decrement = () => {
  if (props.disabled) return
  
  const currentValue = props.modelValue === '' ? 0 : parseInt(props.modelValue) || 0
  const newValue = Math.max(parseInt(props.min), currentValue - 1)
  emit('update:modelValue', newValue)
}

const handleFocus = (event) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event) => {
  isFocused.value = false
  emit('blur', event)
}
</script>

<style scoped>
/* Hide native number input spinners on all devices for consistency */
.number-input-mobile::-webkit-outer-spin-button,
.number-input-mobile::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.number-input-mobile {
  -moz-appearance: textfield;
}

/* Mobile-specific styles */
@media (max-width: 640px) {
  .number-input-mobile {
    /* Ensure input is easily tappable on mobile */
    min-height: 44px;
    font-size: 16px; /* Prevents zoom on iOS */
    padding: 12px;
  }
  
  /* Hide any remaining stepper buttons on mobile */
  .number-input-mobile::-webkit-outer-spin-button,
  .number-input-mobile::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
    display: none;
  }
}

/* Tablet and desktop styles */
@media (min-width: 641px) {
  .number-input-mobile {
    min-height: 38px;
    padding: 8px 12px;
  }
}
</style>
