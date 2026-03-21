# Mobile UI Redesign — Design Spec

**Date:** 2026-03-21
**File:** `web/index.html`
**Scope:** `@media (max-width: 768px)` block only. Desktop styles are untouched.

---

## Problem

The current mobile layout has two structural issues:

1. `.control-group` is absolutely positioned at `bottom: calc(36px + env(safe-area-inset-bottom, 0px))` — a magic 36px offset that hardcodes the expected height of `#session-stats`. This breaks whenever stats content changes height.
2. `#session-stats` and `.control-group` are two separate absolutely-positioned elements that must coordinate their heights, causing gaps and overlaps on real devices.
3. The settings button floats top-right, wasting canvas space and creating a cluttered top bar alongside the results pill.

---

## Design

### Layout skeleton

- `body { display: block }` — no flex layout on mobile.
- `#canvas-container` — `position: absolute; inset: 0; height: 100dvh; z-index: 1`. Canvas fills the entire screen.
- `#sidebar` — `position: absolute; inset: 0; pointer-events: none; background: transparent; box-shadow: none; z-index: 10`. Transparent overlay; only interactive children receive pointer events.

### Top floating pill (`#results-area`)

- `position: absolute; top: calc(env(safe-area-inset-top, 16px) + 8px); left: 50%; transform: translateX(-50%)`
- `background: var(--surface-color); border-radius: 28px; padding: 10px 22px`
- `box-shadow: 0 8px 28px rgba(0,0,0,0.16)`
- `pointer-events: auto; z-index: 20`
- `width: auto; min-width: 220px; max-width: 90vw`
- `#main-guess` font-size reduced to 48px on mobile to prevent overflow.
- `#feedback-area` sits below the emoji with `margin-top: 0`.
- `#correction-ui` uses `position: relative` (no absolute bottom anchoring), so it expands the pill naturally downward when visible. No `bottom: 100%` or similar.

### Bottom drawer (unified)

`.control-group` becomes the single bottom drawer, containing both tools and session stats:

- `position: absolute; bottom: 0; left: 0; right: 0`
- `background: var(--surface-color); border-radius: 22px 22px 0 0`
- `box-shadow: 0 -8px 28px rgba(0,0,0,0.13)`
- `padding: 14px 16px env(safe-area-inset-bottom, 12px) 16px`
- `pointer-events: auto; z-index: 10`

Content rows inside the drawer (top to bottom):

1. **Palette row** — `display: flex; flex-wrap: nowrap; overflow-x: auto; gap: 8px`. Color swatches `36×36px`, `flex: 0 0 auto`. Scrollbar hidden.
2. **Tool row** — `display: flex; gap: 8px`. Three buttons:
   - Eraser (`flex: 1`) — icon + label, uses `tronche_erase.svg` with `--icon-filter`
   - Erase All (`flex: 1`) — icon + label, uses `tronche_eraseall.svg` with `--icon-filter-danger`, `btn-danger` styling
   - Settings (`width: 42px; flex-shrink: 0`) — icon-only, uses `tronche_settings.svg` with `--icon-filter`; replaces the old floating `.settings-btn` on mobile
3. **Stats line** — `#session-stats` repositioned inside the drawer via CSS: `position: static; border-top: 1px solid var(--border-color); padding-top: 8px; text-align: center; font-size: 12px`. The `margin-top: auto` from desktop is removed on mobile.

### Settings popup

- `.settings-popup` on mobile anchors above the drawer rather than relative to the now-removed top-right button. Positioned `bottom: calc(100% + 8px); right: 16px` within the `#sidebar` overlay context.

### Removed on mobile

- `.settings-btn` top-right positioning overrides — the settings icon lives in the tool row instead. The `.settings-btn` element itself stays in the DOM (shared with desktop) but its mobile absolute positioning is removed.
- The old `bottom: calc(36px + ...)` magic offset on `.control-group`.
- `.logo-area`, `.tagline`, `#advanced-stats` remain hidden (`display: none !important`).

### Safe area / notch support

- Pill top uses `env(safe-area-inset-top, 16px)`.
- Drawer bottom padding uses `env(safe-area-inset-bottom, 12px)`.

---

## What is NOT changing

- All CSS outside `@media (max-width: 768px)` — desktop layout is untouched.
- HTML structure — no elements are added, removed, or reordered.
- JavaScript — no changes.
- Dark mode variables — the redesign uses the same CSS custom properties, so dark mode works for free.

---

## Verification

Manual review only (no automated tests for layout):

1. Confirm desktop layout is visually unchanged at >768px.
2. Confirm on mobile (<768px):
   - Canvas fills the full screen behind everything.
   - Pill floats at the top; does not overlap the drawer.
   - Bottom drawer is a single cohesive block with no gap between tools and stats.
   - Settings icon in tool row opens the popup above the drawer.
   - Correction UI expands the pill downward without breaking layout.
   - No content is clipped by device notch or home indicator.
   - Dark mode renders correctly.
