# Mobile UI Redesign — Design Spec

**Date:** 2026-03-21
**File:** `web/index.html`
**Scope:** `@media (max-width: 768px)` CSS block, plus one small HTML change (moving `.settings-btn` and `.settings-popup` inside `.action-row`). Desktop styles and all JavaScript are untouched.

---

## Problem

The current mobile layout has two structural issues:

1. `.control-group` is absolutely positioned at `bottom: calc(36px + env(safe-area-inset-bottom, 0px))` — a magic 36px offset that hardcodes the expected height of `#session-stats`. This breaks whenever stats content changes height.
2. `#session-stats` and `.control-group` are two separate absolutely-positioned elements that must coordinate heights, causing gaps and overlaps on real devices.

Additionally, the settings button floating top-right creates a cluttered top bar alongside the results pill and wastes canvas space.

---

## HTML change (minimal)

Move `.settings-btn` and `.settings-popup` from their current location (siblings of `.control-group` inside `#sidebar`) into `.action-row` inside `.control-group`.

This is required because CSS cannot reorder sibling elements, and the design places the settings icon inside the tool row.

**Desktop safety:** `.settings-btn` currently uses `position: absolute; top: 20px; right: 20px`, resolved relative to `#sidebar` (its nearest positioned ancestor, via `position: relative`). Neither `.action-row` nor `.control-group` set a `position` property on desktop (they remain `position: static`), so `#sidebar` stays the containing block after the move. Desktop appearance is unchanged. **Note:** `.control-group` and `.action-row` must remain `position: static` on desktop — the mobile `position: absolute` override on `.control-group` is scoped inside the media query and does not affect desktop.

The same reasoning applies to `.settings-popup` (`position: absolute; top: 60px; right: 20px`).

---

## CSS changes

All changes are inside `@media (max-width: 768px)` unless noted.

### 1. Layout skeleton

```css
body { display: block; }

#canvas-container {
    position: absolute;
    inset: 0;
    height: 100dvh;
    z-index: 1;
}

#sidebar {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100dvh;
    background: transparent;
    box-shadow: none;
    pointer-events: none;
    z-index: 10;
    padding: 0;
    overflow: hidden;
}
```

### 2. Top floating pill — replace the existing `#results-area` mobile block entirely

The entire existing `#results-area` block (lines 556–575 of the current HTML) is **replaced** with:

```css
#results-area {
    position: absolute;
    top: calc(env(safe-area-inset-top, 0px) + 16px);
    left: 50%;
    transform: translateX(-50%);
    min-height: auto;
    background: var(--surface-color);
    box-sizing: border-box;
    padding: 12px 24px;
    border-radius: 30px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.16);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    z-index: 20;
    pointer-events: auto;
    width: auto;
    min-width: 220px;
    max-width: 90vw;
}

#main-guess {
    font-size: 48px;
    margin: 0;
    line-height: 1;
}

#feedback-area {
    margin-top: 0;
    gap: 12px;
}

#feedback-area .btn {
    padding: 8px 16px;
    font-size: 14px;
}

#correction-ui {
    position: relative;
    bottom: auto;
    left: auto;
    right: auto;
    background: transparent;
    padding: 0;
    margin-top: 4px;
    box-shadow: none;
    width: 100%;
}
```

### 3. Bottom drawer — replace the existing `.control-group` and `#session-stats` mobile blocks entirely

The existing `.control-group` block (lines ~605–619) and the `#session-stats` block (lines ~654–667) are **replaced** with:

```css
.control-group {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--surface-color);
    box-sizing: border-box;
    padding: 14px 16px env(safe-area-inset-bottom, 12px) 16px;
    border-radius: 22px 22px 0 0;
    box-shadow: 0 -8px 28px rgba(0, 0, 0, 0.13);
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 12px;
    pointer-events: auto;
    z-index: 10;
}

.control-group > label { display: none; }

.palette {
    display: flex;
    flex-wrap: nowrap;
    gap: 8px;
    margin-bottom: 0;
    overflow-x: auto;
    padding-bottom: 4px;
    -ms-overflow-style: none;
    scrollbar-width: none;
}
.palette::-webkit-scrollbar { display: none; }

.color-swatch {
    flex: 0 0 auto;
    width: 36px;
    height: 36px;
}

.action-row {
    display: flex;
    gap: 8px;
    margin-bottom: 0;
}

.action-row .tool-btn {
    flex: 1;
    margin-bottom: 0;
    padding: 10px;
    font-size: 14px;
}

/* Settings icon-only button in the tool row */
.action-row .settings-btn {
    position: static;
    width: 42px;
    flex-shrink: 0;
    flex-grow: 0;
    height: auto;
    top: auto;
    right: auto;
}

#session-stats {
    position: static;
    margin-top: 0;
    border-top: 1px solid var(--border-color);
    padding: 8px 0 0 0;
    text-align: center;
    font-size: 12px;
    opacity: 0.8;
}
```

### 4. Settings popup — `position: fixed` to escape `overflow: hidden`

`#sidebar` has `overflow: hidden`. An absolutely-positioned popup descendant would be clipped. The popup must use `position: fixed`:

```css
.settings-popup {
    position: fixed;
    bottom: calc(160px + env(safe-area-inset-bottom, 0px));
    right: 16px;
    top: auto;
    z-index: 30;
}
```

The `160px` base is the estimated drawer height (palette ~58px + tool row ~44px + stats ~20px + top padding ~38px). Adding `env(safe-area-inset-bottom, 0px)` accounts for the home indicator on iPhone/Android, which would otherwise cause the popup to overlap the drawer on notched devices.

### 5. Old rules to remove

These existing rules inside `@media (max-width: 768px)` become dead/incorrect code and **must be deleted**:

- `.settings-btn { top: env(...); right: 16px; }` — replaced by `position: static` in rule 3 above
- `.settings-popup { top: calc(...); right: 16px; z-index: 30; }` — replaced by `position: fixed` in rule 4 above
- Remove `.settings-btn` and `.settings-popup` from the blanket `pointer-events: auto` selector (they are now inside the drawer which already has `pointer-events: auto`)

---

## What is NOT changing

- All CSS outside `@media (max-width: 768px)` — desktop layout is untouched.
- JavaScript — no changes.
- Dark mode — the redesign uses the same CSS custom properties, so dark mode works automatically.
- `.logo-area`, `.tagline`, `#advanced-stats` remain hidden on mobile (`display: none !important`).

---

## Verification

Manual review only (no automated layout tests):

1. Desktop (>768px): layout visually unchanged — sidebar left, canvas right, settings top-right in sidebar. Settings popup opens at the correct desktop position.
2. Mobile (<768px):
   - Canvas fills the full screen behind all overlays.
   - Pill floats at the top with correct safe-area offset; does not overlap the drawer.
   - Bottom drawer is a single cohesive block — no gap or seam between tools and stats.
   - Settings icon in the tool row opens the popup (`position: fixed`) above the drawer with no overlap.
   - Settings popup is not clipped by `#sidebar { overflow: hidden }`.
   - Settings popup does not overlap the pill even when `#correction-ui` is expanded (pill grows downward).
   - Correction UI expands the pill downward without breaking layout.
   - No content clipped by device notch or home indicator (test on iPhone with notch and on Android with gesture bar).
   - Dark mode renders correctly.
