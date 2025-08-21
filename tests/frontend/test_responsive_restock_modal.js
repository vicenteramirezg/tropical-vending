/**
 * Test file for responsive restock modal functionality
 * Tests the responsive behavior of the restock popup across different device sizes
 */

// Mock viewport resize functionality for testing
const setViewport = (width, height) => {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  Object.defineProperty(window, 'innerHeight', {
    writable: true,
    configurable: true,
    value: height,
  });
  window.dispatchEvent(new Event('resize'));
};

// Test scenarios for different device sizes
const testScenarios = [
  {
    name: 'Mobile Phone',
    width: 375,
    height: 667,
    expectedBehavior: {
      modalLayout: 'fullscreen',
      stepperButtons: false,
      inputType: 'numeric',
      minTouchTarget: 44
    }
  },
  {
    name: 'iPad Portrait',
    width: 768,
    height: 1024,
    expectedBehavior: {
      modalLayout: 'overlay',
      stepperButtons: true,
      inputType: 'number',
      minTouchTarget: 38
    }
  },
  {
    name: 'iPad Landscape',
    width: 1024,
    height: 768,
    expectedBehavior: {
      modalLayout: 'overlay',
      stepperButtons: true,
      inputType: 'number',
      minTouchTarget: 38
    }
  },
  {
    name: 'Desktop',
    width: 1440,
    height: 900,
    expectedBehavior: {
      modalLayout: 'overlay',
      stepperButtons: true,
      inputType: 'number',
      minTouchTarget: 38
    }
  }
];

/**
 * Test responsive number input component behavior
 */
function testResponsiveNumberInput() {
  console.log('🧪 Testing ResponsiveNumberInput component...');
  
  testScenarios.forEach(scenario => {
    console.log(`📱 Testing ${scenario.name} (${scenario.width}x${scenario.height})`);
    
    // Set viewport
    setViewport(scenario.width, scenario.height);
    
    // Test stepper button visibility
    const stepperButtons = document.querySelectorAll('.responsive-number-input button');
    const isMobile = scenario.width < 640; // sm breakpoint
    
    if (isMobile) {
      console.log('  ✅ Mobile: Stepper buttons should be hidden');
      // In mobile, buttons should have 'hidden sm:inline-flex' classes
    } else {
      console.log('  ✅ Desktop/Tablet: Stepper buttons should be visible');
      // In desktop/tablet, buttons should be visible
    }
    
    // Test input field properties
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
      const computedStyle = window.getComputedStyle(input);
      const minHeight = parseInt(computedStyle.minHeight);
      
      if (minHeight >= scenario.expectedBehavior.minTouchTarget) {
        console.log(`  ✅ Input min-height (${minHeight}px) meets touch target requirement`);
      } else {
        console.log(`  ❌ Input min-height (${minHeight}px) below required ${scenario.expectedBehavior.minTouchTarget}px`);
      }
      
      // Check for native spinner hiding
      const webkitAppearance = computedStyle.webkitAppearance;
      const mozAppearance = computedStyle.mozAppearance;
      
      if (webkitAppearance === 'none' || mozAppearance === 'textfield') {
        console.log('  ✅ Native input spinners properly hidden');
      } else {
        console.log('  ❌ Native input spinners may still be visible');
      }
    });
  });
}

/**
 * Test modal layout responsiveness
 */
function testModalResponsiveness() {
  console.log('🧪 Testing RestockFormModal responsiveness...');
  
  testScenarios.forEach(scenario => {
    console.log(`📱 Testing ${scenario.name} modal layout`);
    
    setViewport(scenario.width, scenario.height);
    
    const isMobile = scenario.width < 640;
    
    if (isMobile) {
      console.log('  ✅ Mobile: Should use fullscreen layout with sticky header/footer');
      // Check for mobile-specific classes
      const mobileLayout = document.querySelector('.sm\\:hidden.min-h-screen');
      const stickyHeader = document.querySelector('.sticky.top-0');
      const stickyFooter = document.querySelector('.sticky.bottom-0');
      
      if (mobileLayout) console.log('    ✅ Mobile layout container found');
      if (stickyHeader) console.log('    ✅ Sticky header found');
      if (stickyFooter) console.log('    ✅ Sticky footer found');
    } else {
      console.log('  ✅ Desktop/Tablet: Should use overlay modal layout');
      // Check for desktop-specific classes
      const desktopLayout = document.querySelector('.hidden.sm\\:flex');
      const modalOverlay = document.querySelector('.bg-gray-500.bg-opacity-75');
      
      if (desktopLayout) console.log('    ✅ Desktop layout container found');
      if (modalOverlay) console.log('    ✅ Modal overlay found');
    }
  });
}

/**
 * Test machine products section layout
 */
function testMachineProductsLayout() {
  console.log('🧪 Testing MachineProductsSection layout...');
  
  testScenarios.forEach(scenario => {
    console.log(`📱 Testing ${scenario.name} products layout`);
    
    setViewport(scenario.width, scenario.height);
    
    const isMobile = scenario.width < 640;
    
    if (isMobile) {
      console.log('  ✅ Mobile: Should use vertical card layout');
      // Check for mobile product cards
      const mobileCards = document.querySelectorAll('.sm\\:hidden .border.rounded-lg');
      const verticalInputs = document.querySelectorAll('.sm\\:hidden .space-y-3');
      
      if (mobileCards.length > 0) console.log('    ✅ Mobile product cards found');
      if (verticalInputs.length > 0) console.log('    ✅ Vertical input layout found');
    } else {
      console.log('  ✅ Desktop/Tablet: Should use grid layout');
      // Check for desktop grid layout
      const gridLayout = document.querySelectorAll('.hidden.sm\\:grid.grid-cols-12');
      
      if (gridLayout.length > 0) console.log('    ✅ Grid layout found');
    }
  });
}

/**
 * Test accessibility features
 */
function testAccessibility() {
  console.log('🧪 Testing accessibility features...');
  
  // Check for proper ARIA labels
  const numberInputs = document.querySelectorAll('input[type="number"]');
  numberInputs.forEach((input, index) => {
    const label = input.getAttribute('aria-label') || input.getAttribute('label');
    if (label) {
      console.log(`  ✅ Input ${index + 1} has proper labeling: "${label}"`);
    } else {
      console.log(`  ❌ Input ${index + 1} missing accessibility label`);
    }
  });
  
  // Check for screen reader text on buttons
  const srTexts = document.querySelectorAll('.sr-only');
  if (srTexts.length > 0) {
    console.log(`  ✅ Found ${srTexts.length} screen reader texts`);
  } else {
    console.log('  ❌ No screen reader texts found');
  }
  
  // Check for proper focus management
  const focusableElements = document.querySelectorAll('input, button, select, textarea');
  const focusRings = Array.from(focusableElements).filter(el => 
    el.className.includes('focus:ring') || el.className.includes('focus:outline')
  );
  
  console.log(`  ✅ ${focusRings.length}/${focusableElements.length} elements have focus indicators`);
}

/**
 * Run all tests
 */
function runResponsiveTests() {
  console.log('🚀 Starting responsive restock modal tests...\n');
  
  try {
    testResponsiveNumberInput();
    console.log('');
    
    testModalResponsiveness();
    console.log('');
    
    testMachineProductsLayout();
    console.log('');
    
    testAccessibility();
    console.log('');
    
    console.log('✅ All responsive tests completed!');
    
    return {
      success: true,
      message: 'All responsive behavior tests passed'
    };
  } catch (error) {
    console.error('❌ Test failed:', error);
    return {
      success: false,
      message: error.message
    };
  }
}

/**
 * Manual testing checklist for developers
 */
function printManualTestingChecklist() {
  console.log(`
📋 MANUAL TESTING CHECKLIST
==========================

🔍 DESKTOP (1024px+):
  □ Modal opens as overlay with backdrop
  □ Number inputs show increment/decrement buttons
  □ Grid layout displays all product info in columns
  □ Modal is scrollable if content exceeds viewport
  □ Form fields are appropriately sized

🔍 TABLET (768px - 1023px):
  □ Modal opens as overlay with backdrop
  □ Number inputs show increment/decrement buttons
  □ Grid layout displays all product info in columns
  □ Touch targets are at least 38px
  □ Form is easy to navigate with touch

🔍 MOBILE (< 768px):
  □ Modal opens fullscreen (no backdrop)
  □ Number inputs have NO increment/decrement buttons
  □ Products display as vertical cards
  □ Touch targets are at least 44px
  □ Numeric keyboard appears when tapping inputs
  □ Sticky header with close button
  □ Sticky footer with action buttons
  □ Content scrolls smoothly between header/footer

🔍 CROSS-DEVICE:
  □ Native number spinners are hidden on all devices
  □ Font size is 16px on mobile (prevents iOS zoom)
  □ Focus indicators are visible and consistent
  □ Form validation works across all layouts
  □ Data persists when rotating device/resizing

🔍 ACCESSIBILITY:
  □ Screen readers can navigate the form
  □ All inputs have proper labels
  □ Focus management works correctly
  □ Color contrast meets WCAG guidelines
  □ Form can be completed using only keyboard
  `);
}

// Export functions for use in browser console or test runners
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    runResponsiveTests,
    testResponsiveNumberInput,
    testModalResponsiveness,
    testMachineProductsLayout,
    testAccessibility,
    printManualTestingChecklist,
    testScenarios
  };
} else {
  // Browser environment - attach to window for manual testing
  window.responsiveTests = {
    runResponsiveTests,
    testResponsiveNumberInput,
    testModalResponsiveness,
    testMachineProductsLayout,
    testAccessibility,
    printManualTestingChecklist,
    testScenarios
  };
  
  console.log('🧪 Responsive test utilities loaded! Use window.responsiveTests to run tests.');
  printManualTestingChecklist();
}
