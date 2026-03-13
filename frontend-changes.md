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
