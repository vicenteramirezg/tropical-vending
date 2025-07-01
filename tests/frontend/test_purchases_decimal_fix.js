/**
 * Frontend tests for the Purchases component decimal place fix
 */

// Mock purchase form structure
function createMockPurchaseForm() {
    return {
        value: {
            quantity: 1,
            total_cost: 0,
            cost_per_unit: 0
        }
    };
}

// The fixed calculateUnitCost function
function calculateUnitCost(purchaseForm) {
    const quantity = parseFloat(purchaseForm.value.quantity) || 0;
    const totalCost = parseFloat(purchaseForm.value.total_cost) || 0;
    
    if (quantity > 0) {
        // Round to 2 decimal places to match backend validation
        purchaseForm.value.cost_per_unit = Math.round((totalCost / quantity) * 100) / 100;
    } else {
        purchaseForm.value.cost_per_unit = 0;
    }
}

// Test cases
const testCases = [
    { quantity: 3, totalCost: 10.00, expected: 3.33, description: "10.00 / 3 = 3.333... should round to 3.33" },
    { quantity: 7, totalCost: 20.00, expected: 2.86, description: "20.00 / 7 = 2.857142... should round to 2.86" },
    { quantity: 4, totalCost: 8.00, expected: 2.00, description: "8.00 / 4 = 2.00 (exact)" },
    { quantity: 3, totalCost: 5.00, expected: 1.67, description: "5.00 / 3 = 1.666... should round to 1.67" }
];

// Run tests
function runTests() {
    console.log("Testing Decimal Place Fix for Purchases Component\n");
    
    let passed = 0;
    let failed = 0;
    
    testCases.forEach((testCase, index) => {
        const purchaseForm = createMockPurchaseForm();
        purchaseForm.value.quantity = testCase.quantity;
        purchaseForm.value.total_cost = testCase.totalCost;
        
        calculateUnitCost(purchaseForm);
        
        const actual = purchaseForm.value.cost_per_unit;
        const expected = testCase.expected;
        
        console.log(`Test ${index + 1}: ${testCase.description}`);
        console.log(`  Input: ${testCase.quantity} units @ $${testCase.totalCost}`);
        console.log(`  Expected: $${expected}`);
        console.log(`  Actual: $${actual}`);
        
        if (actual === expected) {
            console.log(`  PASSED\n`);
            passed++;
        } else {
            console.log(`  FAILED\n`);
            failed++;
        }
    });
    
    console.log(`Results: ${passed} passed, ${failed} failed`);
    return { passed, failed };
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runTests, calculateUnitCost };
}

// Run if executed directly
if (typeof require !== 'undefined' && require.main === module) {
    runTests();
}
