import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TipAnalysisForm from '../TipAnalysisForm'

describe('TipAnalysisForm Component', () => {
  const mockOnSubmit = vi.fn()
  const user = userEvent.setup()

  beforeEach(() => {
    mockOnSubmit.mockClear()
  })

  it('renders form elements correctly', () => {
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    // Check for form elements
    expect(screen.getByLabelText('Investment Tip Message')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Paste the investment tip/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Analyze Tip' })).toBeInTheDocument()
    
    // Check for sample tips section
    expect(screen.getByText('Try these sample tips:')).toBeInTheDocument()
    expect(screen.getAllByText(/Sample \d+:/)).toHaveLength(3)
    
    // Check for disclaimer
    expect(screen.getByText(/Disclaimer:/)).toBeInTheDocument()
  })

  it('validates message length correctly', async () => {
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByLabelText('Investment Tip Message')
    const submitButton = screen.getByRole('button', { name: 'Analyze Tip' })

    // Test empty message
    await user.click(submitButton)
    expect(screen.getByText('Please enter a message to analyze')).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()

    // Test message too short
    await user.type(textarea, 'short')
    await user.click(submitButton)
    expect(screen.getByText('Message must be at least 10 characters long')).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()

    // Clear and test message too long
    await user.clear(textarea)
    const longMessage = 'x'.repeat(5001)
    await user.type(textarea, longMessage)
    await user.click(submitButton)
    expect(screen.getByText('Message must be less than 5000 characters')).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('submits valid message successfully', async () => {
    mockOnSubmit.mockResolvedValue(undefined)
    
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByLabelText('Investment Tip Message')
    const submitButton = screen.getByRole('button', { name: 'Analyze Tip' })

    const validMessage = 'This is a valid investment tip message for testing purposes'
    await user.type(textarea, validMessage)
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(validMessage)
    })
  })

  it('handles submission errors gracefully', async () => {
    mockOnSubmit.mockRejectedValue(new Error('API Error'))
    
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByLabelText('Investment Tip Message')
    const submitButton = screen.getByRole('button', { name: 'Analyze Tip' })

    await user.type(textarea, 'Valid message for error testing')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Failed to analyze message. Please try again.')).toBeInTheDocument()
    })
  })

  it('displays loading state correctly', () => {
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={true} />)

    const submitButton = screen.getByRole('button', { name: /Analyzing/ })
    expect(submitButton).toBeDisabled()
    expect(screen.getByText('Analyzing...')).toBeInTheDocument()
    
    // Check that textarea is disabled during loading
    const textarea = screen.getByLabelText('Investment Tip Message')
    expect(textarea).toBeDisabled()
    
    // Check that sample buttons are disabled during loading
    const sampleButtons = screen.getAllByText(/Sample \d+:/)
    sampleButtons.forEach(button => {
      expect(button.closest('button')).toBeDisabled()
    })
  })

  it('updates character count correctly', async () => {
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByLabelText('Investment Tip Message')
    
    // Initially should show 0/5000
    expect(screen.getByText('0/5000 characters')).toBeInTheDocument()

    // Type some text
    const testMessage = 'Test message'
    await user.type(textarea, testMessage)
    
    expect(screen.getByText(`${testMessage.length}/5000 characters`)).toBeInTheDocument()
  })

  it('clears form when clear button is clicked', async () => {
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByLabelText('Investment Tip Message')
    
    // Type some text
    await user.type(textarea, 'Some test message')
    
    // Clear button should appear
    const clearButton = screen.getByText('Clear')
    expect(clearButton).toBeInTheDocument()
    
    // Click clear
    await user.click(clearButton)
    
    // Textarea should be empty
    expect(textarea).toHaveValue('')
    expect(screen.getByText('0/5000 characters')).toBeInTheDocument()
  })

  it('loads sample tips when clicked', async () => {
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByLabelText('Investment Tip Message')
    const firstSampleButton = screen.getAllByText(/Sample \d+:/)[0].closest('button')
    
    expect(firstSampleButton).toBeInTheDocument()
    await user.click(firstSampleButton!)

    // Textarea should be populated with sample content
    expect(textarea).not.toHaveValue('')
    
    // Should contain the sample text (checking for part of the known sample)
    expect(textarea.value).toContain('URGENT')
  })

  it('disables submit button when message is empty', async () => {
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    const submitButton = screen.getByRole('button', { name: 'Analyze Tip' })
    
    // Initially disabled (empty message)
    expect(submitButton).toBeDisabled()

    // Type something
    const textarea = screen.getByLabelText('Investment Tip Message')
    await user.type(textarea, 'Valid message')
    
    // Should be enabled now
    expect(submitButton).not.toBeDisabled()

    // Clear the message
    await user.clear(textarea)
    
    // Should be disabled again
    expect(submitButton).toBeDisabled()
  })

  it('clears error when new input is provided', async () => {
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByLabelText('Investment Tip Message')
    const submitButton = screen.getByRole('button', { name: 'Analyze Tip' })

    // Trigger validation error
    await user.click(submitButton)
    expect(screen.getByText('Please enter a message to analyze')).toBeInTheDocument()

    // Type valid message - error should clear
    await user.type(textarea, 'Valid message for testing')
    
    // Error should be gone
    expect(screen.queryByText('Please enter a message to analyze')).not.toBeInTheDocument()
  })

  it('shows disclaimer text', () => {
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    expect(screen.getByText(/This analysis is for informational purposes only/)).toBeInTheDocument()
    expect(screen.getByText(/Always conduct your own research/)).toBeInTheDocument()
  })

  it('handles form submission with Enter key', async () => {
    mockOnSubmit.mockResolvedValue(undefined)
    
    render(<TipAnalysisForm onSubmit={mockOnSubmit} loading={false} />)

    const textarea = screen.getByLabelText('Investment Tip Message')
    
    await user.type(textarea, 'Valid message for testing purposes')
    
    // Submit with Ctrl+Enter (common pattern for textareas)
    await user.type(textarea, '{Control>}{Enter}{/Control}')
    
    // Form should submit
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled()
    })
  })
})