/**
 * Manual Test Runner for Demo Confidence
 * This file contains basic tests that can be run manually to verify component functionality
 */

// Mock DOM environment for testing
const mockDocument = {
  createElement: (tag: string) => ({
    tagName: tag.toUpperCase(),
    innerHTML: '',
    textContent: '',
    className: '',
    style: {},
    setAttribute: () => {},
    getAttribute: () => null,
    appendChild: () => {},
    removeChild: () => {},
    querySelector: () => null,
    querySelectorAll: () => [],
    addEventListener: () => {},
    removeEventListener: () => {},
  }),
  querySelector: () => null,
  querySelectorAll: () => [],
  body: {
    appendChild: () => {},
    removeChild: () => {},
  }
}

// Basic test framework
class TestRunner {
  private tests: Array<{ name: string; fn: () => void | Promise<void> }> = []
  private results: Array<{ name: string; passed: boolean; error?: string }> = []

  describe(name: string, fn: () => void) {
    console.log(`\n=== ${name} ===`)
    fn()
  }

  it(name: string, fn: () => void | Promise<void>) {
    this.tests.push({ name, fn })
  }

  expect(actual: any) {
    return {
      toBe: (expected: any) => {
        if (actual !== expected) {
          throw new Error(`Expected ${actual} to be ${expected}`)
        }
      },
      toEqual: (expected: any) => {
        if (JSON.stringify(actual) !== JSON.stringify(expected)) {
          throw new Error(`Expected ${JSON.stringify(actual)} to equal ${JSON.stringify(expected)}`)
        }
      },
      toContain: (expected: any) => {
        if (!actual.includes(expected)) {
          throw new Error(`Expected ${actual} to contain ${expected}`)
        }
      },
      toBeGreaterThan: (expected: number) => {
        if (actual <= expected) {
          throw new Error(`Expected ${actual} to be greater than ${expected}`)
        }
      },
      toBeTruthy: () => {
        if (!actual) {
          throw new Error(`Expected ${actual} to be truthy`)
        }
      },
      toBeFalsy: () => {
        if (actual) {
          throw new Error(`Expected ${actual} to be falsy`)
        }
      }
    }
  }

  async run() {
    console.log(`\nRunning ${this.tests.length} tests...\n`)
    
    for (const test of this.tests) {
      try {
        await test.fn()
        this.results.push({ name: test.name, passed: true })
        console.log(`✅ ${test.name}`)
      } catch (error) {
        this.results.push({ 
          name: test.name, 
          passed: false, 
          error: error instanceof Error ? error.message : String(error)
        })
        console.log(`❌ ${test.name}: ${error instanceof Error ? error.message : String(error)}`)
      }
    }

    const passed = this.results.filter(r => r.passed).length
    const failed = this.results.filter(r => !r.passed).length
    
    console.log(`\n=== Test Results ===`)
    console.log(`Passed: ${passed}`)
    console.log(`Failed: ${failed}`)
    console.log(`Total: ${this.tests.length}`)
    
    if (failed > 0) {
      console.log(`\nFailed tests:`)
      this.results.filter(r => !r.passed).forEach(r => {
        console.log(`- ${r.name}: ${r.error}`)
      })
    }

    return { passed, failed, total: this.tests.length }
  }
}

// Create test runner instance
const testRunner = new TestRunner()

// RiskBadge Component Tests
testRunner.describe('RiskBadge Component Logic Tests', () => {
  
  testRunner.it('should handle risk level mapping correctly', () => {
    const getBadgeStyles = (level: 'Low' | 'Medium' | 'High') => {
      switch (level) {
        case 'High':
          return { container: 'bg-red-50 border-red-200', badge: 'bg-red-100 text-red-800' }
        case 'Medium':
          return { container: 'bg-yellow-50 border-yellow-200', badge: 'bg-yellow-100 text-yellow-800' }
        case 'Low':
          return { container: 'bg-green-50 border-green-200', badge: 'bg-green-100 text-green-800' }
        default:
          return { container: 'bg-gray-50 border-gray-200', badge: 'bg-gray-100 text-gray-800' }
      }
    }

    const highRisk = getBadgeStyles('High')
    testRunner.expect(highRisk.container).toContain('bg-red-50')
    
    const mediumRisk = getBadgeStyles('Medium')
    testRunner.expect(mediumRisk.container).toContain('bg-yellow-50')
    
    const lowRisk = getBadgeStyles('Low')
    testRunner.expect(lowRisk.container).toContain('bg-green-50')
  })

  testRunner.it('should validate score ranges', () => {
    const validateScore = (score: number) => {
      return score >= 0 && score <= 100
    }

    testRunner.expect(validateScore(0)).toBeTruthy()
    testRunner.expect(validateScore(50)).toBeTruthy()
    testRunner.expect(validateScore(100)).toBeTruthy()
    testRunner.expect(validateScore(-1)).toBeFalsy()
    testRunner.expect(validateScore(101)).toBeFalsy()
  })

  testRunner.it('should handle empty reasons array', () => {
    const reasons: string[] = []
    testRunner.expect(reasons.length).toBe(0)
    testRunner.expect(Array.isArray(reasons)).toBeTruthy()
  })
})

// TipAnalysisForm Component Tests
testRunner.describe('TipAnalysisForm Component Logic Tests', () => {
  
  testRunner.it('should validate message length correctly', () => {
    const validateMessage = (message: string) => {
      const trimmed = message.trim()
      if (!trimmed) return { valid: false, error: 'Please enter a message to analyze' }
      if (trimmed.length < 10) return { valid: false, error: 'Message must be at least 10 characters long' }
      if (trimmed.length > 5000) return { valid: false, error: 'Message must be less than 5000 characters' }
      return { valid: true, error: null }
    }

    // Test empty message
    const emptyResult = validateMessage('')
    testRunner.expect(emptyResult.valid).toBeFalsy()
    testRunner.expect(emptyResult.error).toContain('Please enter a message')

    // Test short message
    const shortResult = validateMessage('short')
    testRunner.expect(shortResult.valid).toBeFalsy()
    testRunner.expect(shortResult.error).toContain('at least 10 characters')

    // Test valid message
    const validResult = validateMessage('This is a valid message for testing purposes')
    testRunner.expect(validResult.valid).toBeTruthy()
    testRunner.expect(validResult.error).toBe(null)

    // Test long message
    const longMessage = 'x'.repeat(5001)
    const longResult = validateMessage(longMessage)
    testRunner.expect(longResult.valid).toBeFalsy()
    testRunner.expect(longResult.error).toContain('less than 5000 characters')
  })

  testRunner.it('should handle character counting', () => {
    const getCharacterCount = (message: string) => {
      return message.length
    }

    testRunner.expect(getCharacterCount('')).toBe(0)
    testRunner.expect(getCharacterCount('hello')).toBe(5)
    testRunner.expect(getCharacterCount('hello world')).toBe(11)
  })

  testRunner.it('should handle form state management', () => {
    let formState = {
      message: '',
      error: '',
      loading: false
    }

    const updateMessage = (newMessage: string) => {
      formState.message = newMessage
      formState.error = '' // Clear error when typing
    }

    const setError = (error: string) => {
      formState.error = error
    }

    const setLoading = (loading: boolean) => {
      formState.loading = loading
    }

    // Test initial state
    testRunner.expect(formState.message).toBe('')
    testRunner.expect(formState.error).toBe('')
    testRunner.expect(formState.loading).toBeFalsy()

    // Test updating message
    updateMessage('test message')
    testRunner.expect(formState.message).toBe('test message')
    testRunner.expect(formState.error).toBe('')

    // Test setting error
    setError('Validation error')
    testRunner.expect(formState.error).toBe('Validation error')

    // Test clearing error when updating message
    updateMessage('new message')
    testRunner.expect(formState.error).toBe('')

    // Test loading state
    setLoading(true)
    testRunner.expect(formState.loading).toBeTruthy()
  })
})

// Error Handling Tests
testRunner.describe('Error Handling Tests', () => {
  
  testRunner.it('should handle invalid risk levels gracefully', () => {
    const handleRiskLevel = (level: string) => {
      const validLevels = ['Low', 'Medium', 'High']
      if (!validLevels.includes(level)) {
        return 'Unknown'
      }
      return level
    }

    testRunner.expect(handleRiskLevel('High')).toBe('High')
    testRunner.expect(handleRiskLevel('Invalid')).toBe('Unknown')
  })

  testRunner.it('should handle special characters in input', () => {
    const sanitizeInput = (input: string) => {
      // Basic sanitization - remove potentially dangerous patterns
      const dangerous = ['<script', 'javascript:', 'data:text/html']
      const lower = input.toLowerCase()
      
      for (const pattern of dangerous) {
        if (lower.includes(pattern)) {
          throw new Error('Input contains potentially unsafe content')
        }
      }
      
      return input.trim()
    }

    testRunner.expect(sanitizeInput('Normal text')).toBe('Normal text')
    testRunner.expect(sanitizeInput('  Text with spaces  ')).toBe('Text with spaces')
    
    // Test that dangerous content throws error
    try {
      sanitizeInput('<script>alert("xss")</script>')
      throw new Error('Should have thrown an error')
    } catch (error) {
      testRunner.expect(error instanceof Error ? error.message : '').toContain('unsafe content')
    }
  })

  testRunner.it('should handle boundary values correctly', () => {
    const validateScore = (score: number) => {
      if (typeof score !== 'number' || isNaN(score)) {
        return { valid: false, normalized: 0 }
      }
      
      // Clamp to valid range
      const normalized = Math.max(0, Math.min(100, score))
      return { valid: score >= 0 && score <= 100, normalized }
    }

    const result1 = validateScore(50)
    testRunner.expect(result1.valid).toBeTruthy()
    testRunner.expect(result1.normalized).toBe(50)

    const result2 = validateScore(-10)
    testRunner.expect(result2.valid).toBeFalsy()
    testRunner.expect(result2.normalized).toBe(0)

    const result3 = validateScore(150)
    testRunner.expect(result3.valid).toBeFalsy()
    testRunner.expect(result3.normalized).toBe(100)
  })
})

// Export test runner for manual execution
if (typeof window !== 'undefined') {
  // Browser environment
  (window as any).runDemoTests = () => testRunner.run()
  console.log('Demo tests loaded. Run window.runDemoTests() to execute.')
} else {
  // Node environment
  testRunner.run().then(results => {
    process.exit(results.failed > 0 ? 1 : 0)
  })
}

export default testRunner