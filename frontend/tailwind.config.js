/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    // Ensure opacity modifiers are included
    { pattern: /bg-(primary|secondary|accent|background|contrast)-(50|100|200|300|400|500|600|700|800|900)\/(5|10|20|25|30|40|50|60|70|75|80|90|95|100)/ },
    { pattern: /text-(primary|secondary|accent|background|contrast)-(50|100|200|300|400|500|600|700|800|900)\/(5|10|20|25|30|40|50|60|70|75|80|90|95|100)/ },
    { pattern: /border-(primary|secondary|accent|background|contrast)-(50|100|200|300|400|500|600|700|800|900)\/(5|10|20|25|30|40|50|60|70|75|80|90|95|100)/ },
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Jost', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'Noto Sans', 'sans-serif'],
      },
      fontWeight: {
        'medium': '500',
      },
      colors: {
        // Dark Theme Colors
        dark: {
          primary: '#0a0a0a',     // Deep black for main backgrounds
          secondary: '#1a1a1a',   // Dark gray for cards and sections
          accent: '#ccff00',      // Bright lime green for buttons and CTAs
          background: '#0f0f0f',  // Slightly lighter black for containers
          text: '#e5e5e5',       // Light gray for readable text
          border: '#333333',     // Border color for dark theme
          hover: '#2a2a2a',      // Hover states
          muted: '#666666',      // Muted text
        },
        // Refined Purple Professional Palette
        primary: {
          50: '#faf5ff',  // Lightest
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#ddd6fe',
          400: '#c4b5fd',
          500: '#6b46c1', // Base color - Navigation, headers, main CTAs
          600: '#8b7bd8', // Lighter than base
          700: '#a594e0', // Even lighter
          800: '#bfade8', // Much lighter
          900: '#d9c7f0', // Lightest shade
        },
        secondary: {
          50: '#faf5ff', // Ultra Light Purple - Main background, content areas
          100: '#f3e8ff', // Light Lavender - Light background sections
          200: '#e9d5ff',
          300: '#ddd6fe', // Soft Purple - Card backgrounds, secondary areas
          400: '#c4b5fd',
          500: '#a78bfa',
          600: '#8b5cf6', // Royal Purple - Accent elements, highlights
          700: '#7c3aed',
          800: '#6d28d9',
          900: '#5b21b6',
        },
        accent: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#9333ea', // Medium Purple - Primary elements, buttons
          600: '#8b5cf6', // Royal Purple - Accent elements, highlights
          700: '#7c3aed',
          800: '#6d28d9',
          900: '#4c1d95', // Dark Purple - Strong contrast elements
        },
        background: {
          50: '#ffffff', // Pure White - Text, clean backgrounds
          100: '#faf5ff', // Ultra Light Purple - Main page background, content containers
          200: '#f3e8ff', // Light Lavender - Light background sections
          300: '#e9d5ff',
          400: '#ddd6fe', // Soft Purple - Card backgrounds, secondary areas
          500: '#c4b5fd',
          600: '#a78bfa',
          700: '#8b5cf6',
          800: '#7c3aed',
          900: '#6d28d9',
        },
        contrast: {
          50: '#ffffff', // Pure White - Text, clean backgrounds
          100: '#f9fafb',
          200: '#f3f4f6',
          300: '#e5e7eb',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#000000', // Pure Black - Contrast sections, text
        },
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
      },
      backgroundImage: {
        // Custom gradient combinations
        'gradient-sphere': 'linear-gradient(135deg, #ddd6fe 0%, #8b5cf6 100%)', // 3D Sphere Gradient
        'gradient-button': 'linear-gradient(135deg, #9333ea 0%, #6b46c1 100%)', // Button Gradient
        'gradient-background': 'linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)', // Background Gradient
        'gradient-card': 'linear-gradient(135deg, #f3e8ff 0%, #ddd6fe 100%)', // Card Gradient
        'gradient-hero': 'linear-gradient(135deg, #6b46c1 0%, #9333ea 50%, #8b5cf6 100%)', // Hero Section
      },
    },
  },
  plugins: [],
}