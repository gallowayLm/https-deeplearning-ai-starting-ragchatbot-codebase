# Frontend Changes

## Code Quality Tooling Setup

### New Files Added

#### `frontend/package.json`
Defines the frontend as an npm package and provides quality scripts:
- `npm run format` — auto-format all HTML/CSS/JS files with Prettier
- `npm run format:check` — check formatting without modifying files (CI-safe)
- `npm run lint` — run ESLint on `script.js`
- `npm run lint:fix` — auto-fix ESLint violations in `script.js`
- `npm run quality` — run both `format:check` and `lint` together (full quality gate)

**DevDependencies:**
- `prettier@^3.3.3` — opinionated code formatter (the JS/HTML/CSS equivalent of black)
- `eslint@^8.57.0` — JavaScript linter

#### `frontend/.prettierrc`
Prettier configuration enforcing consistent formatting across all frontend files:
- Single quotes for strings
- Semicolons required
- 4-space indentation (matches existing codebase style)
- 100-character print width
- Trailing commas in ES5 positions (arrays, objects)
- LF line endings

#### `frontend/.eslintrc.json`
ESLint configuration for JavaScript quality checks:
- Targets browser environment with ES2021 globals
- Extends `eslint:recommended` ruleset
- `marked` declared as a readonly global (loaded via CDN)
- Key rules enforced:
  - `no-var` (error) — require `const`/`let`
  - `prefer-const` (warning) — prefer `const` when variable is not reassigned
  - `eqeqeq` (error) — require `===` over `==`
  - `no-multiple-empty-lines` (error) — max 1 consecutive blank line
  - `no-trailing-spaces` (error) — no trailing whitespace
  - `semi` (error) — semicolons required
  - `quotes` (error) — single quotes required

### Files Modified

#### `frontend/script.js`
Fixed formatting inconsistencies:
- Removed double blank line between event listener block and `// Suggested questions` comment (line ~32)
- Removed double blank line between `setupEventListeners()` closing brace and `// Chat Functions` comment (line ~43)

### How to Use

Install dependencies (one-time setup):
```bash
cd frontend
npm install
```

Run quality checks:
```bash
npm run quality        # check formatting + lint
npm run format         # auto-fix formatting
npm run lint:fix       # auto-fix lint issues
```

---

## Feature: Light/Dark Theme Toggle Button

### Summary
Added a fixed-position icon-based toggle button (sun/moon) for switching between dark and light themes. The button matches the existing design aesthetic, includes smooth transitions, and is fully accessible.

---

### Files Modified

#### `frontend/index.html`
- Added a `<button id="themeToggle">` element at the bottom of `<body>` (before scripts), containing:
  - A **sun SVG icon** (shown in dark mode — signals "switch to light")
  - A **moon SVG icon** (shown in light mode — signals "switch to dark")
  - `aria-label` and `title` attributes for accessibility

#### `frontend/style.css`
1. **CSS Reset** (`*, *::before, *::after`): Added `transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease` so all elements smoothly animate when the theme changes.

2. **Light Theme Variables** (`[data-theme="light"]`): Overrides the dark-mode `:root` variables:
   - `--background`: `#f8fafc`
   - `--surface`: `#ffffff`
   - `--surface-hover`: `#e2e8f0`
   - `--text-primary`: `#0f172a`
   - `--text-secondary`: `#64748b`
   - `--border-color`: `#cbd5e1`
   - `--assistant-message`: `#e9eef5`
   - `--shadow`: lightened shadow
   - Code/pre blocks: reduced background opacity for light mode readability

3. **`.theme-toggle` styles**:
   - Fixed position: top-right corner (`top: 1rem; right: 1rem`)
   - 44×44px circular button matching the surface/border design tokens
   - Hover: scale up slightly + deeper shadow
   - Focus: blue focus ring (`var(--focus-ring)`) for keyboard navigation
   - Active: slight scale-down press feedback

4. **Icon animation**:
   - Both icons are `position: absolute` and transition `opacity` + `transform`
   - Dark mode: sun icon visible, moon rotated/hidden
   - Light mode: moon icon visible, sun rotated/hidden
   - Transition: `opacity 0.3s ease, transform 0.4s ease` for a smooth swap

#### `frontend/script.js`
- Added `themeToggle` to DOM element cache
- Added `initTheme()`: reads `localStorage` → falls back to `prefers-color-scheme` media query → applies theme on page load
- Added `applyTheme(theme)`: sets `data-theme` on `<html>` and updates `aria-label` on the button
- Added `toggleTheme()`: flips between `dark`/`light`, persists to `localStorage`
- Wired `themeToggle.addEventListener('click', toggleTheme)` in `setupEventListeners()`

---

### Behaviour
- **Default**: respects OS `prefers-color-scheme`; falls back to dark if no preference
- **Persistence**: choice saved in `localStorage` under key `theme`
- **Accessibility**: button has `aria-label` (dynamically updated to describe the *next* action), icons marked `aria-hidden="true"`, standard focus ring, keyboard-activatable via Enter/Space
- **Animation**: all background, color, and border transitions animate smoothly at 0.3s; icon swap has a rotate+fade at 0.4s
