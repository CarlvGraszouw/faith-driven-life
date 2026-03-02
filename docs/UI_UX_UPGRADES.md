# UI/UX upgrades — world-class look and feel

This document summarizes the progressive enhancements applied across the site for a polished, modern experience while keeping accessibility and performance in mind.

## Design system (tokens)

- **CSS custom properties** added for consistency:
  - `--radius-sm`, `--radius-md`, `--radius-lg` — border radius
  - `--shadow-sm`, `--shadow-md`, `--shadow-glow` — elevation and accent glow
  - `--transition-fast`, `--transition-smooth` — animation timing
  - `--surface-hover` — hover state for surfaces
- **Reduced motion**: All transitions shorten to `0.01s` when the user has `prefers-reduced-motion: reduce` (system or browser setting).

## Typography

- **Fluid type**: Section titles and intro title use `clamp()` so they scale smoothly between small and large viewports.
- **Letter-spacing**: Slight negative letter-spacing on headings for a refined look.

## Micro-interactions

- **Navigation**: Links and pill buttons (Blogs, Resources) use smooth color and border transitions; pill buttons keep the existing glow pulse.
- **Cards**: Audio cards and approved-item cards get a subtle lift (`translateY(-2px)`) and stronger shadow on hover (only when reduced motion is off).
- **Buttons**: Play button scales slightly on hover; submit buttons have a light scale on hover/active.
- **Links**: Page-links and resource links use color transitions; explore links get a small `translateX(4px)` on hover.
- **Footer**: “Back to top” and other links use consistent transition on color.

## Depth and polish

- **Nav bar**: Semi-transparent background with `backdrop-filter: blur(12px)` where supported (glass effect). Fallback: solid background.
- **Cards**: Consistent border radius from tokens; intro verse and daily devotional use shared shadow variables.
- **Daily devotional**: Hover state adds a subtle gold glow to the box shadow.

## Page load and scroll reveal

- **Load**: Main content fades in on first paint (opacity 0 → 1) after a single animation frame so the page doesn’t “pop” in. Disabled when `prefers-reduced-motion: reduce`.
- **Scroll reveal**: Sections with class `reveal` start slightly below and faded; when they enter the viewport (Intersection Observer), they animate to full opacity and position. Also disabled when reduced motion is requested.

## Accessibility

- Existing **focus-visible** outlines (accent color) are unchanged.
- **Skip link** uses the same transition tokens and radius.
- All motion respects **prefers-reduced-motion** so users who need less animation still get a stable, readable layout.

## Pages updated

- **index.html**: Full set of tokens, nav glass, card/link/button micro-interactions, scroll reveal on intro and page-links, load fade-in.
- **blogs.html**: Tokens, nav glass, fluid section title, link transitions, load fade-in, scroll reveal on main section.
- **resources.html**: Tokens, nav glass, fluid section title, resource and study link transitions, load fade-in, scroll reveal on main section.

## Optional next steps

- Add the same tokens and nav glass to **book.html**, **audio.html**, **bible.html**, **comments.html**, **prayer-requests.html**, **testimonies.html**, and **post.html** for full-site consistency.
- Consider a shared `styles.css` (or design-tokens.css) so future changes apply everywhere from one place.
