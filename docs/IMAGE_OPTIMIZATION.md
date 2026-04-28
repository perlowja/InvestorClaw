# InvestorClaw Image Optimization

## Overview

InvestorClaw uses aggressive image compression and modern formats (WebP) to ensure fast CDN delivery on GitHub/GitLab.

## Asset Sizes

| Asset | Before | After | Reduction |
|-------|--------|-------|-----------|
| eod-report-sample.jpg | 1.2 MB | ~300 KB | 75% |
| stonkmode-banner.jpg | 442 KB | ~120 KB | 73% |
| investorclaw-logo.jpg | 51 KB | ~15 KB | 71% |

## Format Strategy

**Primary**: WebP (modern, ~40% smaller than JPG)
**Fallback**: Progressive JPEG (quality 75)
**Avatars**: SVG (scalable, already optimized at ~3KB each)

## HTML Implementation

All images use `<picture>` with WebP + JPEG fallback and `loading="lazy"`:

```html
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="..." loading="lazy"/>
</picture>
```

Benefits:
- WebP: ~40% smaller file size
- Lazy loading: defers load until image is visible
- Progressive JPEG: renders during download
- Fallback: works in older browsers

## Running Optimization

```bash
# Compress all JPGs and create WebP versions
./scripts/optimize-images.sh
```

Requirements:
- `imagemagick`: `brew install imagemagick`
- `webp`: `brew install webp`
- `pngquant`: `brew install pngquant` (optional, for PNG compression)

## CDN Performance

**GitLab CDN (before optimization)**:
- eod-report-sample: ~5-8 seconds
- stonkmode-banner: ~2-3 seconds

**Expected (after WebP + lazy loading)**:
- eod-report-sample: ~500-800ms
- stonkmode-banner: ~300-500ms
- Total page load improvement: 80-85%

## Avatars

Stonkmode avatars remain as SVG (2-3KB each) because:
- Already minimal size
- Vector format = scales perfectly
- No quality loss
- No conversion needed
