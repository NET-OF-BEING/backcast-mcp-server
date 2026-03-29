# Backcasting Dashboard Makeover — Design Spec

**Date:** 2026-03-29
**Direction:** Refined Dark — polish the existing dark theme to Linear/Raycast quality
**Scope:** Full visual overhaul + 8 new features
**File:** `http_server.py` (single-file SPA embedded in Flask, lines ~406–1340)

---

## Design System

### Color Tokens

```
--bg:            #08080c
--surface-0:     #0c0c14      (sidebar, header backgrounds)
--surface-1:     #111119      (cards, panels)
--surface-2:     #181824      (hover states, inputs)
--surface-3:     #222233      (active pills, elevated elements)
--border:        rgba(255,255,255,0.06)
--border-hover:  rgba(255,255,255,0.12)
--accent:        #7c5cfc
--accent-light:  #9b7dff
--accent-glow:   rgba(124,92,252,0.2)
--accent-subtle: rgba(124,92,252,0.08)
--success:       #34d399
--success-subtle:rgba(52,211,153,0.08)
--warning:       #fbbf24
--error:         #f87171
--text-primary:  #eaeaf0
--text-secondary:#8888a0
--text-muted:    #50506a
```

Light theme overrides (same token names, swapped values):

```
--bg:            #f8f8fc
--surface-0:     #ffffff
--surface-1:     #ffffff
--surface-2:     #f0f0f6
--surface-3:     #e8e8f0
--border:        rgba(0,0,0,0.08)
--border-hover:  rgba(0,0,0,0.15)
--accent:        #6b4ce6
--accent-light:  #8b6cf0
--accent-glow:   rgba(107,76,230,0.15)
--accent-subtle: rgba(107,76,230,0.06)
--text-primary:  #1a1a2e
--text-secondary:#6b6b80
--text-muted:    #9898ac
```

### Typography

- Font: `Inter`, system fallbacks
- Body: 14px, line-height 1.5
- Plan title: 26px, weight 700, tracking -0.03em
- Section labels: 11px, weight 600, uppercase, tracking 0.06em
- Step title: 14px, weight 500
- Stats values: 20-28px, weight 700, tracking -0.02em

### Spacing

- 8px base grid
- Card padding: 16-20px
- Section gaps: 28px
- Sidebar padding: 12-20px
- Main content padding: 32px

### Border Radius

- Cards/panels: 12px (`--radius`)
- Buttons/inputs: 8px (`--radius-sm`)
- Pills/badges: 999px (full round)

### Effects

- Ambient glow: radial gradient from accent at top center, 6% opacity
- Card hover: translateY(-1px) + box-shadow 0 4px 16px rgba(0,0,0,0.2)
- Button press: scale(0.97)
- All transitions: 150ms ease
- Accent button shadow: 0 2px 8px var(--accent-glow)

---

## Layout Structure

### Sidebar (260px, collapsible)

1. **Brand header** — icon (gradient square with layers SVG) + "Backcasting" text + collapse button
2. **Plan list** — items with dot indicator, active state uses accent-subtle bg + accent-light text
3. **Footer** — dashed border "+ New Plan" button that turns accent on hover

**Collapsed state:** 60px wide, shows only brand icon + plan dot indicators. Tooltip on hover for plan names. Smooth 200ms slide transition. State persisted to localStorage.

### Top Header Bar

Fixed bar with:
- **Left:** Search box with magnifying glass icon + "/" keyboard hint
- **Right:** Theme toggle (sun/moon SVG), keyboard shortcuts icon, export dropdown

### Main Content Area

Scrollable area containing:
1. **Plan header** — title (26px) + meta line (step count · timeline · completion %)
2. **Stats row** — progress ring card + 3 mini stat cards
3. **Action bar** — primary "Add Step" button, secondary buttons, filter pills (right-aligned)
4. **Step list** — scrollable card list with drag handles

---

## Feature Specifications

### 1. Animated Progress Ring

- **Element:** SVG circle with `stroke-dasharray`/`stroke-dashoffset` animation
- **Size:** 100x100px in a card alongside status breakdown
- **Gradient:** linear-gradient from accent (#7c5cfc) to success (#34d399)
- **Animation:** stroke-dashoffset transitions over 800ms with `cubic-bezier(0.4, 0, 0.2, 1)` on load and status changes
- **Center label:** percentage (28px bold) + "Done" subtitle (11px muted)
- **Breakdown:** 4 rows beside the ring — Completed/In Progress/Blocked/To Do with colored dots and counts
- **Replaces:** flat progress bar + 5-column stats grid

### 2. Collapsible Sidebar

- **Toggle:** button in sidebar brand header (◁/▷ arrow)
- **Collapsed width:** 60px — shows brand icon, plan dots only
- **Animation:** CSS transition on `grid-template-columns` (200ms ease)
- **Tooltips:** plan names appear as title attribute on hover when collapsed
- **Persistence:** `localStorage.setItem('sidebar-collapsed', 'true'|'false')`
- **Mobile:** sidebar fully hidden below 768px, toggle button in main header

### 3. Drag-to-Reorder Steps

- **Handle:** 6-dot grip icon, left side of each step card
- **Visibility:** opacity 0 by default, fades in on card hover
- **Implementation:** HTML5 Drag and Drop API (no library needed for this list size)
- **Drag state:** dragged card gets opacity 0.5 + accent border, drop zone shows 2px accent line
- **On drop:** call `PUT /api/plan/reorder` with `{step_id, new_position}`, save, refresh
- **Backend:** new `/api/plan/reorder` endpoint that reorders `current_plan.steps` list

### 4. Expandable Step Cards

- **Default:** compact single-line card (title + truncated description + priority badge)
- **Expand trigger:** click anywhere on the card body (not on action buttons or drag handle)
- **Expanded view:** bordered card with accent highlight, 2-column grid showing:
  - Description (full text)
  - Resources needed
  - Dependencies
  - Risks
- **Animation:** max-height transition 200ms
- **Only one expanded at a time** — clicking another card collapses the current one
- **Data source:** step objects already have `resources`, `risks`, `dependencies` fields from the backend

### 5. Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `n` | Open "New Plan" modal |
| `s` | Open "Add Step" modal |
| `j/k` | Navigate up/down step list (visual selection ring) |
| `1` | Mark selected step "in_progress" |
| `2` | Mark selected step "completed" |
| `3` | Mark selected step "blocked" |
| `/` | Focus search box |
| `Escape` | Close modal / deselect / blur search |
| `?` | Show shortcuts overlay |

- **Visual hint:** persistent bottom-right badge showing `? Shortcuts`
- **Shortcuts overlay:** modal listing all keys, dismissed by `?` or Escape
- **Guard:** shortcuts disabled when a modal is open or input is focused (except Escape)

### 6. Search & Filter Steps

- **Search bar:** in top header, filters steps by title/description as you type (client-side)
- **Filter pills:** segmented control in action bar — All / To Do / Active / Done / Blocked
- **Active pill styling:** `--surface-3` bg + `--text-primary` color
- **Behavior:** search + filter combine (AND). Empty results show "No matching steps" empty state
- **Debounce:** 150ms on search input keystrokes

### 7. Dark/Light Theme Toggle

- **Toggle:** sun/moon SVG icon button in header
- **Implementation:** `[data-theme="light"]` selector on `<html>` element overrides CSS custom properties
- **Transition:** 200ms transition on background-color and color properties to avoid flash
- **Persistence:** `localStorage.setItem('theme', 'dark'|'light')`
- **Default:** dark (current)
- **Light tokens:** defined in Design System section above

### 8. Completion Celebrations

- **Step done:** small confetti burst (20-30 particles) from the status ring position
- **100% plan completion:** large confetti burst (100+ particles) from center of viewport + toast "All steps complete!"
- **Implementation:** lightweight canvas-based confetti (inline, no library — ~40 lines of JS)
- **Particles:** random colors from [accent, success, warning, accent-light], gravity + fade, 1.5s duration
- **Respects `prefers-reduced-motion`:** skip animation, show only the toast

---

## Step Card Redesign (Detail)

### Compact State (default)
```
[drag-handle] [status-ring] [title + truncated-desc] [priority-badge] [hover-actions]
```

- **Drag handle:** 6 dots in 2x3 grid, `cursor: grab`, visible on hover only
- **Status ring:** 22px circle — empty (todo), filled dot (in progress), checkmark (done), exclamation (blocked)
- **Title:** 14px weight 500. Completed steps get `text-decoration: line-through` with muted color
- **Description:** 12px muted, `text-overflow: ellipsis`, single line
- **Priority badge:** pill with status-appropriate background tint
- **Hover actions:** 3 small icon buttons (▶ Start, ✓ Done, ⚠ Block), fade in on hover

### Status Ring Interactions

- Click the ring directly to cycle: not_started → in_progress → completed → not_started
- Or use the hover action buttons for explicit state setting

---

## Modal Improvements

- Backdrop: `rgba(0,0,0,0.6)` + `backdrop-filter: blur(12px)`
- Card: `--surface-1` bg, 12px radius, 1px border, `box-shadow: 0 24px 48px rgba(0,0,0,0.4)`
- Close button: 32x32 with hover state
- Form labels: 12px, weight 500, secondary color
- Inputs: surface-2 bg, accent border + glow on focus
- Submit: full-width accent button

No structural changes needed — current modals already follow this pattern closely. Just tighten the visual tokens.

---

## Accessibility

- All interactive elements have visible focus rings (2px accent outline, 3px offset)
- Ghost/muted button text: minimum #8a8a9f on surface-1 (#111119) = ~4.7:1 contrast (AA pass)
- Keyboard navigation: full tab order through sidebar → header → action bar → step list
- Step action buttons: `aria-label` attributes ("Mark step 27 as completed")
- Search input: `aria-label="Search steps"`
- Filter pills: `role="tablist"` + `role="tab"` + `aria-selected`
- `prefers-reduced-motion`: disable confetti, progress ring animation, card hover transforms
- Theme toggle: `aria-label` updates to "Switch to light/dark theme"

---

## Backend Changes

One new endpoint:

```
PUT /api/plan/reorder
Body: { "step_id": int, "new_position": int }
Response: { "status": "success" }
```

Reorders `current_plan.steps` list by removing the step and inserting at `new_position`. Auto-saves.

No other backend changes needed — all other features are client-side only.

---

## Out of Scope

- Mobile-native app
- Multi-user / real-time collaboration
- Undo/redo system
- Step dependencies visualization (graph view)
- Offline support
- Responsive tablet layout (existing 768px breakpoint is sufficient)
