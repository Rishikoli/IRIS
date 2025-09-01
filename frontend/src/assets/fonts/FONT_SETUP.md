# Merchant Black Font Setup

## 📋 Required Font Files

To use the Merchant Black font in your deployed application, you need to add the following font files to this directory:

```
frontend/src/assets/fonts/
├── MerchantBlack.woff2  (preferred - best compression)
├── MerchantBlack.woff   (fallback for older browsers)
├── MerchantBlack.ttf    (fallback for very old browsers)
└── merchant-black.css   (already created)
```

## 🔧 How to Add Font Files

### Step 1: Convert Your Font
If you only have `.otf` or `.ttf` files, convert them to web formats:
- Use online converters like [Font Squirrel Webfont Generator](https://www.fontsquirrel.com/tools/webfont-generator)
- Or use [CloudConvert](https://cloudconvert.com/ttf-to-woff2)

### Step 2: Add Files to Project
1. Copy your converted font files to `frontend/src/assets/fonts/`
2. Make sure the filenames match what's in `merchant-black.css`:
   - `MerchantBlack.woff2`
   - `MerchantBlack.woff`
   - `MerchantBlack.ttf`

### Step 3: Verify Setup
The font is already imported in `HomePage.tsx` and will work once you add the font files.

## 🚀 Deployment Notes

- ✅ **Will work on Vercel**: Once font files are added to the project
- ✅ **Will work on any hosting**: Font files are bundled with your app
- ✅ **No external dependencies**: Self-hosted fonts load faster
- ✅ **Offline support**: Fonts work without internet connection

## 🎨 Usage

The font is already configured with the `.merchant-black` CSS class:

```jsx
<h1 className="merchant-black">IRIS</h1>
```

## 📝 Current Status

- ✅ CSS configuration: Ready
- ✅ Component integration: Complete
- ⏳ Font files: **Need to be added by you**

Once you add the font files, the Merchant Black font will display correctly on all deployments!