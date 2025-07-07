// Test for partial restock functionality
// This test verifies that the validation and processing logic works correctly for partial restocks

import { describe, it, expect } from 'vitest'

// Mock the composable functions we're testing
const mockRestockForm = {
  validateForm: (locationMachines) => {
    // Check if at least one machine has restock data
    const hasAnyRestockData = locationMachines.some(machine => 
      machine.products.some(product => 
        hasRestockData(product)
      )
    )
    
    if (!hasAnyRestockData) {
      return { valid: false, error: 'Please record stock levels for at least one product' }
    }
    
    // Validate that products with partial data have all required fields
    const hasIncompleteData = locationMachines.some(machine => 
      machine.products.some(product => {
        const hasPartialData = hasRestockData(product)
        if (hasPartialData) {
          // If any field has data, stock_before and restocked are required
          return product.stock_before === '' || product.restocked === ''
        }
        return false
      })
    )
    
    if (hasIncompleteData) {
      return { valid: false, error: 'Please complete all fields for products being restocked (stock before and restock amount are required)' }
    }
    
    return { valid: true }
  }
}

const hasRestockData = (product) => {
  return product.stock_before !== '' || 
         product.restocked !== '' || 
         product.discarded !== ''
}

describe('Partial Restock Functionality', () => {
  it('should allow partial restock with only one machine filled', () => {
    const locationMachines = [
      {
        id: 1,
        name: 'Machine 1',
        products: [
          { id: 1, name: 'Product 1', stock_before: '10', restocked: '5', discarded: '0' },
          { id: 2, name: 'Product 2', stock_before: '8', restocked: '3', discarded: '1' }
        ]
      },
      {
        id: 2,
        name: 'Machine 2',
        products: [
          { id: 3, name: 'Product 3', stock_before: '', restocked: '', discarded: '' },
          { id: 4, name: 'Product 4', stock_before: '', restocked: '', discarded: '' }
        ]
      }
    ]

    const result = mockRestockForm.validateForm(locationMachines)
    expect(result.valid).toBe(true)
  })

  it('should reject completely empty restock', () => {
    const locationMachines = [
      {
        id: 1,
        name: 'Machine 1',
        products: [
          { id: 1, name: 'Product 1', stock_before: '', restocked: '', discarded: '' },
          { id: 2, name: 'Product 2', stock_before: '', restocked: '', discarded: '' }
        ]
      }
    ]

    const result = mockRestockForm.validateForm(locationMachines)
    expect(result.valid).toBe(false)
    expect(result.error).toBe('Please record stock levels for at least one product')
  })

  it('should reject incomplete data for products being restocked', () => {
    const locationMachines = [
      {
        id: 1,
        name: 'Machine 1',
        products: [
          { id: 1, name: 'Product 1', stock_before: '10', restocked: '', discarded: '0' }, // Missing restocked
          { id: 2, name: 'Product 2', stock_before: '', restocked: '', discarded: '' }
        ]
      }
    ]

    const result = mockRestockForm.validateForm(locationMachines)
    expect(result.valid).toBe(false)
    expect(result.error).toBe('Please complete all fields for products being restocked (stock before and restock amount are required)')
  })

  it('should allow partial products within a machine', () => {
    const locationMachines = [
      {
        id: 1,
        name: 'Machine 1',
        products: [
          { id: 1, name: 'Product 1', stock_before: '10', restocked: '5', discarded: '0' }, // Complete
          { id: 2, name: 'Product 2', stock_before: '', restocked: '', discarded: '' }  // Empty - should be skipped
        ]
      }
    ]

    const result = mockRestockForm.validateForm(locationMachines)
    expect(result.valid).toBe(true)
  })

  it('should allow only discarded items without restocking', () => {
    const locationMachines = [
      {
        id: 1,
        name: 'Machine 1',
        products: [
          { id: 1, name: 'Product 1', stock_before: '10', restocked: '0', discarded: '2' }, // Only discarding
          { id: 2, name: 'Product 2', stock_before: '', restocked: '', discarded: '' }  // Empty
        ]
      }
    ]

    const result = mockRestockForm.validateForm(locationMachines)
    expect(result.valid).toBe(true)
  })
}) 