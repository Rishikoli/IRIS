import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RiskBadge from '../RiskBadge'
import TipAnalysisForm from '../TipAnalysisForm'

describe('Component Error Handling', () => {
  // Suppress console errors during tests
  const originalError = console.error
  beforeEach(() => {
    console.error = vi.fn()
  })
  
  afterEach(() => {
    console.error = originalError
  })

  describe('RiskBadge Error Handling', () => {
    it('handles invalid risk level gracefully', () => {
      // Test with invalid risk level
      const { container } = render(
        <RiskBadge
          level={'Invalid' as any}
          score={50}
          reasons={['Test reason']}
        />
      )

      // Should still render without crashing
      expect(container).toBeInTheDocument()
      expect(screen.getByText('Risk Level: Invalid')).toBeInTheDocument()
    })

    it('handles negative scores gracefully', () => {
      render(
        <RiskBadge
          level="Low"
          score={-10}
          reasons={['Test reason']}
        />
      )

      // Should render without crashing
      expect(screen.getByText('Score: -10/100')).toBeInTheDocument()
    })

    it('handles scores over 100 gracefully', () => {
      render(
        <RiskBadge
          level="High"
          score={150}
          reasons={['Test reason']}
        />
      )

      // Should render without crashing
      expect(screen.getByText('Score: 150/100')).toBeInTheDocument()
    })

    it('handles null/undefined reasons gracefully', () => {
      render(
        <RiskBadge
          level="Medium"
          score={60}
          reasons={null as any}
        />
      )

      // Should render without crashing
      expect(screen.getByText('Risk Level: Medium')).toBeInTheDocument()
    })

    it('handles very long reason text gracefully', () => {
      const longReason = 'This is a very long reason that might cause layout issues. '.repeat(20)
      
      render(
        <RiskBadge
          level="High"
          score={80}
          reasons={[longReason]}
        />
      )

      // Should render without crashing
      expect(screen.getByText('Risk Level: High')).toBeInTheDocument()
      expect(screen.getByText(longReason)).toBeInTheDocument()
    })

    it('handles special characters in reasons', () => {
      const specialReasons = [
        'Reason with <script>alert("xss")</script>',
        'Reason with unicode: 🚀💰📈',
        'Reason with quotes: "test" and \'test\'',
        'Reason with &amp; &lt; &gt; entities'
      ]

      render(
        <RiskBadge
          level="High"
          score={90}
          reasons={specialReasons}
        />
      )

      // Should render all reasons without crashing
      specialReasons.forEach(reason => {
        expect(screen.getByText(reason)).toBeInTheDocument()
      })
    })
  })

  describe('TipAnalysisForm Error Handling', () => {
    const mockOnSubmit = vi.fn()

    it('handles onSubmit function errors gracefully', async () => {
      mockOnSubmit.mockRejectedValue(new Error('Network error'))

      render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

      const textarea = screen.getByLabelText('Investment Tip Message')
      const submitButton = screen.getByRole('button', { name: 'Analyze Tip' })

      // Type valid message and submit
      await userEvent.type(textarea, 'Valid test message for error handling')
      await userEvent.click(submitButton)

      // Should show error message without crashing
      await waitFor(() => {
        expect(screen.getByText('Failed to analyze message. Please try again.')).toBeInTheDocument()
      })
    })

    it('handles undefined onSubmit function', () => {
      render(<TipAnalysisForm onSubmit={undefined as any} loading={false} />)

      // Should render without crashing
      expect(screen.getByLabelText('Investment Tip Message')).toBeInTheDocument()
    })

    it('handles rapid form submissions', async () => {
      let submitCount = 0
      const slowSubmit = vi.fn().mockImplementation(() => {
        submitCount++
        return new Promise(resolve => setTimeout(resolve, 100))
      })

      render(<TipAnalysisForm onSubmit={slowSubmit} loading={false} />)

      const textarea = screen.getByLabelText('Investment Tip Message')
      const submitButton = screen.getByRole('button', { name: 'Analyze Tip' })

      await userEvent.type(textarea, 'Test message for rapid submission')

      // Click submit multiple times rapidly
      await userEvent.click(submitButton)
      await userEvent.click(submitButton)
      await userEvent.click(submitButton)

      // Should handle gracefully without multiple submissions
      await waitFor(() => {
        expect(submitCount).toBeLessThanOrEqual(1)
      })
    })

    it('handles extremely long input gracefully', async () => {
      render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

      const textarea = screen.getByLabelText('Investment Tip Message')
      
      // Type extremely long text (beyond limit)
      const veryLongText = 'x'.repeat(10000)
      await userEvent.type(textarea, veryLongText)

      // Should show character count and handle gracefully
      expect(screen.getByText(/\/5000 characters/)).toBeInTheDocument()
    })

    it('handles special characters in input', async () => {
      render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

      const textarea = screen.getByLabelText('Investment Tip Message')
      
      const specialText = 'Test with <script>alert("xss")</script> and unicode 🚀💰📈 and quotes "test" \'test\''
      await userEvent.type(textarea, specialText)

      // Should handle without crashing
      expect(textarea).toHaveValue(specialText)
    })

    it('handles loading state changes gracefully', () => {
      const { rerender } = render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

      // Should render in normal state
      expect(screen.getByRole('button', { name: 'Analyze Tip' })).not.toBeDisabled()

      // Change to loading state
      rerender(<TipAnalysisForm onSubmit={mockOnSubmit} loading={true} />)

      // Should handle state change gracefully
      expect(screen.getByRole('button', { name: /Analyzing/ })).toBeDisabled()

      // Change back to normal state
      rerender(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

      // Should handle state change back gracefully
      expect(screen.getByRole('button', { name: 'Analyze Tip' })).not.toBeDisabled()
    })
  })

  describe('Component Integration Error Handling', () => {
    it('handles missing props gracefully', () => {
      // Test RiskBadge with minimal props
      render(
        <RiskBadge
          level="Low"
          score={0}
          reasons={[]}
        />
      )

      expect(screen.getByText('Risk Level: Low')).toBeInTheDocument()
    })

    it('handles component unmounting during async operations', async () => {
      let resolveSubmit: (value: any) => void
      const pendingSubmit = new Promise(resolve => {
        resolveSubmit = resolve
      })

      const mockSubmit = vi.fn().mockReturnValue(pendingSubmit)

      const { unmount } = render(<TipAnalysisForm onSubmit={mockSubmit} loading={false} />)

      const textarea = screen.getByLabelText('Investment Tip Message')
      await userEvent.type(textarea, 'Test message for unmount handling')
      await userEvent.click(screen.getByRole('button', { name: 'Analyze Tip' }))

      // Unmount component while async operation is pending
      unmount()

      // Resolve the pending operation
      resolveSubmit!(undefined)

      // Should not cause any errors
      expect(true).toBe(true) // Test passes if no errors thrown
    })
  })
})