import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import RiskBadge from '../RiskBadge'

describe('RiskBadge Component', () => {
  const mockReasons = [
    'Unrealistic return promises',
    'Urgency pressure tactics',
    'Guaranteed returns claim'
  ]

  it('renders high risk badge correctly', () => {
    render(
      <RiskBadge
        level="High"
        score={95}
        reasons={mockReasons}
      />
    )

    // Check if risk level is displayed
    expect(screen.getByText('Risk Level: High')).toBeInTheDocument()
    
    // Check if score is displayed
    expect(screen.getByText('Score: 95/100')).toBeInTheDocument()
    
    // Check if reasons are displayed
    mockReasons.forEach(reason => {
      expect(screen.getByText(reason)).toBeInTheDocument()
    })
    
    // Check if high risk warning is displayed
    expect(screen.getByText(/High Risk Warning/)).toBeInTheDocument()
    expect(screen.getByText(/Exercise extreme caution/)).toBeInTheDocument()
  })

  it('renders medium risk badge correctly', () => {
    render(
      <RiskBadge
        level="Medium"
        score={65}
        reasons={['Some suspicious patterns detected']}
      />
    )

    expect(screen.getByText('Risk Level: Medium')).toBeInTheDocument()
    expect(screen.getByText('Score: 65/100')).toBeInTheDocument()
    expect(screen.getByText(/Caution Required/)).toBeInTheDocument()
    expect(screen.getByText(/verify the source/)).toBeInTheDocument()
  })

  it('renders low risk badge correctly', () => {
    render(
      <RiskBadge
        level="Low"
        score={25}
        reasons={['Informational content detected']}
      />
    )

    expect(screen.getByText('Risk Level: Low')).toBeInTheDocument()
    expect(screen.getByText('Score: 25/100')).toBeInTheDocument()
    expect(screen.getByText(/Low Risk/)).toBeInTheDocument()
    expect(screen.getByText(/do your own research/)).toBeInTheDocument()
  })

  it('applies correct CSS classes for high risk', () => {
    const { container } = render(
      <RiskBadge
        level="High"
        score={90}
        reasons={mockReasons}
      />
    )

    // Check for red color classes (high risk)
    const badgeContainer = container.querySelector('.bg-red-50')
    expect(badgeContainer).toBeInTheDocument()
  })

  it('applies correct CSS classes for medium risk', () => {
    const { container } = render(
      <RiskBadge
        level="Medium"
        score={60}
        reasons={['Medium risk factor']}
      />
    )

    // Check for yellow color classes (medium risk)
    const badgeContainer = container.querySelector('.bg-yellow-50')
    expect(badgeContainer).toBeInTheDocument()
  })

  it('applies correct CSS classes for low risk', () => {
    const { container } = render(
      <RiskBadge
        level="Low"
        score={30}
        reasons={['Low risk factor']}
      />
    )

    // Check for green color classes (low risk)
    const badgeContainer = container.querySelector('.bg-green-50')
    expect(badgeContainer).toBeInTheDocument()
  })

  it('handles empty reasons array', () => {
    render(
      <RiskBadge
        level="Low"
        score={20}
        reasons={[]}
      />
    )

    expect(screen.getByText('Risk Level: Low')).toBeInTheDocument()
    expect(screen.getByText('Score: 20/100')).toBeInTheDocument()
    
    // Should still show the "Risk Factors Detected:" header
    expect(screen.getByText('Risk Factors Detected:')).toBeInTheDocument()
  })

  it('applies custom className when provided', () => {
    const { container } = render(
      <RiskBadge
        level="High"
        score={85}
        reasons={mockReasons}
        className="custom-class"
      />
    )

    const badgeContainer = container.querySelector('.custom-class')
    expect(badgeContainer).toBeInTheDocument()
  })

  it('displays correct icons for each risk level', () => {
    // Test High risk icon (warning triangle)
    const { rerender } = render(
      <RiskBadge level="High" score={90} reasons={['High risk']} />
    )
    expect(document.querySelector('svg')).toBeInTheDocument()

    // Test Medium risk icon (info circle)
    rerender(
      <RiskBadge level="Medium" score={60} reasons={['Medium risk']} />
    )
    expect(document.querySelector('svg')).toBeInTheDocument()

    // Test Low risk icon (check circle)
    rerender(
      <RiskBadge level="Low" score={30} reasons={['Low risk']} />
    )
    expect(document.querySelector('svg')).toBeInTheDocument()
  })

  it('handles boundary score values correctly', () => {
    // Test minimum score
    const { rerender } = render(
      <RiskBadge level="Low" score={0} reasons={['No risk']} />
    )
    expect(screen.getByText('Score: 0/100')).toBeInTheDocument()

    // Test maximum score
    rerender(
      <RiskBadge level="High" score={100} reasons={['Maximum risk']} />
    )
    expect(screen.getByText('Score: 100/100')).toBeInTheDocument()
  })
})