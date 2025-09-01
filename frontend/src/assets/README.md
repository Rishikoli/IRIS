# Assets Directory

This directory contains all static assets for the IRIS RegTech Platform frontend application.

## Directory Structure

```
assets/
├── backgrounds/     # Background images, patterns, textures
├── data/           # Static data files (JSON, etc.)
├── fonts/          # Custom font files
├── icons/          # UI icons and symbols
├── images/         # Legacy image organization
│   ├── icons/      # (Legacy) UI icons
│   ├── illustrations/ # (Legacy) Illustrations and graphics
│   └── logos/      # (Legacy) Logo files
├── logos/          # IRIS platform logos and branding
├── videos/         # Video assets
└── index.ts        # Central export file for all assets
```

## Usage

### Importing Assets
Use the central index file for clean imports:

```typescript
// Good ✅
import { irisLogo, dashboardIcon, heroBg } from '@/assets'

// Avoid ❌
import irisLogo from '../assets/logos/iris-logo.svg'
```

### Adding New Assets

1. **Place files in appropriate folders** based on type and purpose
2. **Update the index.ts file** to export your new assets
3. **Follow naming conventions**:
   - Use kebab-case for file names
   - Use descriptive, consistent names
   - Include size/variant suffixes when needed

### Asset Guidelines

- **Optimize for web**: Compress images and use appropriate formats
- **Provide multiple formats**: WebP for modern browsers, fallbacks for older ones
- **Use vector formats**: SVG for icons and logos when possible
- **Consistent sizing**: Follow design system specifications
- **Accessibility**: Include alt text and proper contrast ratios

## File Naming Conventions

- **Logos**: `iris-logo-[variant].svg` (e.g., `iris-logo-light.svg`)
- **Icons**: `[name]-icon.svg` (e.g., `dashboard-icon.svg`)
- **Backgrounds**: `[context]-bg.[ext]` (e.g., `hero-bg.jpg`)
- **Videos**: `[context]-video.[ext]` (e.g., `demo-video.mp4`)

## Performance Considerations

- Keep file sizes reasonable for web delivery
- Use lazy loading for large images
- Provide responsive image variants when needed
- Consider using CDN for large assets in production