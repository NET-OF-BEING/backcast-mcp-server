# Dashboard Makeover Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the backcasting dashboard from functional-but-basic to a polished, Linear-quality dark UI with 8 new features.

**Architecture:** Single-file SPA (`http_server.py` lines ~406–1340) with HTML/CSS/JS embedded in a Python string. All changes are CSS + HTML template + JS within `DASHBOARD_HTML`. One new backend endpoint for drag-reorder. The file is already ~1340 lines; we'll work within this structure since it's the established pattern.

**Tech Stack:** Flask backend, vanilla JS frontend, CSS custom properties for theming, SVG for progress ring, HTML5 Drag and Drop API, Canvas API for confetti.

**Spec:** `docs/superpowers/specs/2026-03-29-dashboard-makeover-design.md`

---

## File Map

- **Modify:** `http_server.py:406-1340` — the `DASHBOARD_HTML` string (CSS, HTML, JS)
- **Modify:** `http_server.py:113-145` — `get_all_steps()` to include `resources_needed`, `risks` in detail response
- **Modify:** `http_server.py:231-250` — add reorder endpoint after `update_step_status`

---

## Chunk 1: Design System Foundation + Layout Restructure

Tasks 1–3 establish the new color tokens, typography, layout grid, sidebar, and header. After this chunk the dashboard has its new skeleton but no new features yet.

### Task 1: Replace CSS Custom Properties and Base Styles

**Files:**
- Modify: `http_server.py:412-456` (`:root` block, `body`, `body::before`)

- [ ] **Step 1: Replace the `:root` block with new design tokens**

Replace lines 415–433 (the existing `:root` variables) with:

```css
:root {
    --bg: #08080c;
    --surface-0: #0c0c14;
    --surface-1: #111119;
    --surface-2: #181824;
    --surface-3: #222233;
    --border: rgba(255,255,255,0.06);
    --border-hover: rgba(255,255,255,0.12);
    --accent: #7c5cfc;
    --accent-light: #9b7dff;
    --accent-glow: rgba(124,92,252,0.2);
    --accent-subtle: rgba(124,92,252,0.08);
    --success: #34d399;
    --success-subtle: rgba(52,211,153,0.08);
    --warning: #fbbf24;
    --error: #f87171;
    --text-primary: #eaeaf0;
    --text-secondary: #8888a0;
    --text-muted: #50506a;
    --radius: 12px;
    --radius-sm: 8px;
    --transition: 150ms ease;
}

[data-theme="light"] {
    --bg: #f8f8fc;
    --surface-0: #ffffff;
    --surface-1: #ffffff;
    --surface-2: #f0f0f6;
    --surface-3: #e8e8f0;
    --border: rgba(0,0,0,0.08);
    --border-hover: rgba(0,0,0,0.15);
    --accent: #6b4ce6;
    --accent-light: #8b6cf0;
    --accent-glow: rgba(107,76,230,0.15);
    --accent-subtle: rgba(107,76,230,0.06);
    --success: #22b47f;
    --success-subtle: rgba(34,180,127,0.08);
    --warning: #d4960c;
    --error: #e04545;
    --text-primary: #1a1a2e;
    --text-secondary: #6b6b80;
    --text-muted: #9898ac;
}
```

- [ ] **Step 2: Update `body` styles**

Replace the body rule with:

```css
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: var(--bg);
    min-height: 100vh;
    color: var(--text-primary);
    font-size: 14px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    overflow: hidden;
}
```

- [ ] **Step 3: Replace `body::before` noise texture with ambient glow**

Replace the `body::before` rule with:

```css
body::before {
    content: '';
    position: fixed;
    top: -200px;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 400px;
    background: radial-gradient(ellipse, rgba(124,92,252,0.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

[data-theme="light"] body::before {
    background: radial-gradient(ellipse, rgba(107,76,230,0.04) 0%, transparent 70%);
}
```

- [ ] **Step 4: Verify the server starts and dashboard loads**

Run: `cd /home/panda/Documents/PythonScripts/OutcomeBackcasting && python http_server.py &`
Open: `http://localhost:8080`
Expected: Dashboard loads with darker background, updated colors. Layout may look broken (we fix that next).
Kill: `kill %1`

- [ ] **Step 5: Commit**

```bash
cd /home/panda/Documents/PythonScripts/OutcomeBackcasting
git add http_server.py
git commit -m "style: replace CSS tokens with refined dark design system + light theme"
```

---

### Task 2: Restructure Layout — Sidebar, Header, Main

**Files:**
- Modify: `http_server.py` — CSS section for `.layout`, `.sidebar`, `.main` and HTML structure

- [ ] **Step 1: Replace layout and sidebar CSS**

Remove ALL existing CSS rules for: `.layout`, `@media`, `.sidebar`, `.sidebar-header`, `.sidebar-title`, `.plan-list`, `.plan-item` (lines ~464–522).

Replace with:

```css
.layout {
    display: grid;
    grid-template-columns: 260px 1fr;
    height: 100vh;
    position: relative;
    z-index: 1;
    transition: grid-template-columns 200ms ease;
}
.layout.collapsed { grid-template-columns: 60px 1fr; }

@media (max-width: 768px) {
    .layout { grid-template-columns: 1fr; }
    .sidebar { display: none; }
    .sidebar.mobile-open { display: flex; position: fixed; inset: 0; z-index: 50; width: 280px; }
}

/* Sidebar */
.sidebar {
    background: var(--surface-0);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition: all 200ms ease;
}

.sidebar-brand {
    padding: 20px 20px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
}
.collapsed .sidebar-brand { padding: 16px 12px; justify-content: center; }

.brand-mark {
    display: flex;
    align-items: center;
    gap: 10px;
    overflow: hidden;
}

.brand-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--accent), var(--accent-light));
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 8px var(--accent-glow);
}
.brand-icon svg { width: 18px; height: 18px; color: white; stroke: white; fill: none; }

.brand-name {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: -0.02em;
    white-space: nowrap;
}
.collapsed .brand-name { display: none; }

.collapse-btn {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    transition: all 150ms;
    flex-shrink: 0;
}
.collapse-btn:hover { background: var(--surface-2); color: var(--text-secondary); }
.collapsed .collapse-btn { display: none; }

.sidebar-section {
    padding: 16px 12px;
    flex: 1;
    overflow-y: auto;
}

.sidebar-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    padding: 0 8px;
    margin-bottom: 8px;
}
.collapsed .sidebar-label { display: none; }

.plan-list { list-style: none; display: flex; flex-direction: column; gap: 2px; }

.plan-item {
    padding: 10px 12px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 150ms;
    color: var(--text-secondary);
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 8px;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
    font-family: inherit;
}
.plan-item:hover { background: var(--surface-2); color: var(--text-primary); }
.plan-item.active {
    background: var(--accent-subtle);
    color: var(--accent-light);
    font-weight: 500;
}
.plan-item .plan-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-muted);
    flex-shrink: 0;
}
.plan-item.active .plan-dot { background: var(--accent); box-shadow: 0 0 6px var(--accent-glow); }
.plan-item .plan-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.collapsed .plan-name { display: none; }
.collapsed .plan-item { justify-content: center; padding: 10px 0; }

.sidebar-footer {
    padding: 12px;
    border-top: 1px solid var(--border);
    flex-shrink: 0;
}

.new-plan-btn {
    width: 100%;
    padding: 10px;
    border-radius: var(--radius-sm);
    border: 1px dashed var(--border-hover);
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 13px;
    font-family: inherit;
    transition: all 150ms;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}
.new-plan-btn:hover { border-color: var(--accent); color: var(--accent-light); background: var(--accent-subtle); }
.collapsed .new-plan-btn span { display: none; }
```

- [ ] **Step 2: Add main area + header CSS**

Add these rules after the sidebar section:

```css
/* Main area */
.main {
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.main-header {
    padding: 12px 32px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--surface-0);
    flex-shrink: 0;
}

.header-left { display: flex; align-items: center; gap: 16px; }

.search-box {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--surface-1);
    color: var(--text-muted);
    font-size: 13px;
    min-width: 220px;
    cursor: text;
    transition: all 150ms;
}
.search-box:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
.search-box input {
    border: none;
    background: none;
    color: var(--text-primary);
    font-size: 13px;
    font-family: inherit;
    outline: none;
    flex: 1;
    min-width: 0;
}
.search-box input::placeholder { color: var(--text-muted); }
.search-box kbd {
    font-size: 11px;
    padding: 1px 5px;
    border-radius: 4px;
    background: var(--surface-3);
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-family: inherit;
}
.search-box svg { flex-shrink: 0; color: var(--text-muted); }

.header-right { display: flex; align-items: center; gap: 6px; }

.icon-btn {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 150ms;
    font-size: 16px;
    font-family: inherit;
}
.icon-btn:hover { background: var(--surface-2); color: var(--text-primary); }
.icon-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

.main-scroll {
    flex: 1;
    overflow-y: auto;
    padding: 32px;
}
```

- [ ] **Step 3: Replace HTML structure — sidebar**

Replace the entire `<div class="layout">` through `</aside>` (lines ~1003–1020) with:

```html
<div class="layout" id="appLayout">
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-brand">
            <div class="brand-mark">
                <div class="brand-icon">
                    <svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
                </div>
                <span class="brand-name">Backcasting</span>
            </div>
            <button class="collapse-btn" onclick="toggleSidebar()" aria-label="Collapse sidebar">◁</button>
        </div>
        <div class="sidebar-section">
            <div class="sidebar-label">Plans</div>
            <ul class="plan-list" id="planList">
                <li style="padding:16px;color:var(--text-muted);">Loading plans...</li>
            </ul>
        </div>
        <div class="sidebar-footer">
            <button class="new-plan-btn" onclick="showCreateModal()">+<span> New Plan</span></button>
        </div>
    </aside>
```

- [ ] **Step 4: Replace HTML structure — main area with header**

Replace `<main class="main">` through the opening of `#planDetails` (lines ~1022–1028) with:

```html
    <div class="main">
        <header class="main-header">
            <div class="header-left">
                <div class="search-box">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                    <input type="text" id="searchInput" placeholder="Search steps..." aria-label="Search steps">
                    <kbd>/</kbd>
                </div>
            </div>
            <div class="header-right">
                <button class="icon-btn" onclick="toggleTheme()" id="themeToggle" aria-label="Toggle theme" title="Toggle theme">
                    <svg id="themeIcon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                </button>
                <button class="icon-btn" onclick="showShortcuts()" aria-label="Keyboard shortcuts" title="Keyboard shortcuts">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M6 8h.001M10 8h.001M14 8h.001M18 8h.001M8 12h.001M12 12h.001M16 12h.001M7 16h10"/></svg>
                </button>
            </div>
        </header>

        <div class="main-scroll">
            <div id="noPlanSelected" class="empty-state">
                <h2>Select or create a plan</h2>
                <p>Choose a plan from the sidebar to get started</p>
            </div>

            <div id="planDetails" style="display:none;">
```

- [ ] **Step 5: Update closing tags to match new structure**

Replace `</main>` (after the modals closing) with `</div></div>` to close `.main-scroll` and `.main`.

Ensure the closing `</div>` for `.layout` is still present after `</aside>` content and `</div>` for `.main`.

- [ ] **Step 6: Update `loadPlans()` to use new plan-item markup**

Replace the `loadPlans` function's innerHTML template:

```javascript
list.innerHTML = data.plans.map(p =>
    `<li class="plan-item" onclick="loadPlan('${p}')" title="${p.replace('.json','')}"><span class="plan-dot"></span><span class="plan-name">${p.replace('.json','')}</span></li>`
).join('');
```

Empty state:
```javascript
list.innerHTML = '<li style="padding:16px;color:var(--text-muted);font-size:13px;">No plans yet</li>';
```

- [ ] **Step 7: Verify layout renders correctly**

Run: `cd /home/panda/Documents/PythonScripts/OutcomeBackcasting && python http_server.py &`
Open: `http://localhost:8080`
Expected: Sidebar with brand icon + plan list + new plan button. Header with search box and icon buttons. Main content area below header.
Kill: `kill %1`

- [ ] **Step 8: Commit**

```bash
cd /home/panda/Documents/PythonScripts/OutcomeBackcasting
git add http_server.py
git commit -m "feat: restructure layout with branded sidebar and header bar"
```

---

### Task 3: Redesign Stats Area — Progress Ring + Mini Stats

**Files:**
- Modify: `http_server.py` — CSS for stats, HTML for plan details area, JS for `refreshPlanView`

- [ ] **Step 1: Remove old stats CSS, add new stats CSS**

Remove all CSS rules for: `.progress-bar`, `.progress-fill`, `.stats-grid`, `.stat-card`, `.stat-indicator`, `.stat-value`, `.stat-label`.

Add:

```css
/* Stats row */
.stats-row {
    display: flex;
    gap: 16px;
    margin-bottom: 28px;
}

.progress-ring-card {
    background: var(--surface-1);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 24px;
    min-width: 280px;
    flex-shrink: 0;
}

.ring-container {
    position: relative;
    width: 100px;
    height: 100px;
    flex-shrink: 0;
}

.ring-svg { width: 100px; height: 100px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: var(--surface-3); stroke-width: 8; }
.ring-progress {
    fill: none;
    stroke: url(#ringGradient);
    stroke-width: 8;
    stroke-linecap: round;
    stroke-dasharray: 251.2;
    stroke-dashoffset: 251.2;
    transition: stroke-dashoffset 800ms cubic-bezier(0.4, 0, 0.2, 1);
}

.ring-label {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.ring-value { font-size: 28px; font-weight: 700; letter-spacing: -0.03em; line-height: 1; }
.ring-subtitle { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 2px; }

.ring-details { display: flex; flex-direction: column; gap: 10px; }
.ring-detail { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--text-secondary); }
.ring-detail .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.ring-detail .count { font-weight: 600; color: var(--text-primary); margin-left: auto; min-width: 20px; text-align: right; }

.mini-stats { display: flex; flex: 1; gap: 12px; }

.mini-stat {
    flex: 1;
    background: var(--surface-1);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    position: relative;
    overflow: hidden;
}
.mini-stat::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.mini-stat.stat-next::before { background: var(--success); }
.mini-stat.stat-blocked::before { background: var(--error); }
.mini-stat.stat-timeline::before { background: var(--warning); }

.mini-stat-value { font-size: 20px; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 4px; }
.mini-stat-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }

@media (max-width: 900px) {
    .stats-row { flex-direction: column; }
    .mini-stats { flex-direction: row; }
}
```

- [ ] **Step 2: Replace stats HTML in `#planDetails`**

Remove the old `<div class="progress-bar">` and `<div class="stats-grid">` blocks. Replace with:

```html
<div class="stats-row">
    <div class="progress-ring-card">
        <div class="ring-container">
            <svg class="ring-svg" viewBox="0 0 100 100">
                <defs>
                    <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="var(--accent)"/>
                        <stop offset="100%" stop-color="var(--success)"/>
                    </linearGradient>
                </defs>
                <circle class="ring-bg" cx="50" cy="50" r="40"/>
                <circle class="ring-progress" id="ringProgress" cx="50" cy="50" r="40"/>
            </svg>
            <div class="ring-label">
                <span class="ring-value" id="ringPercent">0%</span>
                <span class="ring-subtitle">Done</span>
            </div>
        </div>
        <div class="ring-details">
            <div class="ring-detail"><span class="dot" style="background:var(--success)"></span>Completed<span class="count" id="statDone">0</span></div>
            <div class="ring-detail"><span class="dot" style="background:var(--accent)"></span>In Progress<span class="count" id="statProgress">0</span></div>
            <div class="ring-detail"><span class="dot" style="background:var(--error)"></span>Blocked<span class="count" id="statBlocked">0</span></div>
            <div class="ring-detail"><span class="dot" style="background:var(--text-muted)"></span>To Do<span class="count" id="statTodo">0</span></div>
        </div>
    </div>
    <div class="mini-stats">
        <div class="mini-stat stat-next">
            <div class="mini-stat-value" id="statNextActions">0</div>
            <div class="mini-stat-label">Next Actions</div>
        </div>
        <div class="mini-stat stat-blocked">
            <div class="mini-stat-value" id="statBlockedCount">0</div>
            <div class="mini-stat-label">Blocked</div>
        </div>
        <div class="mini-stat stat-timeline">
            <div class="mini-stat-value" id="statTimeline">—</div>
            <div class="mini-stat-label">Timeline</div>
        </div>
    </div>
</div>
```

- [ ] **Step 3: Update `refreshPlanView()` to drive the ring and mini stats**

In `refreshPlanView()`, replace the lines that set `progressBar`, `statPercent`, `statDone`, `statProgress`, `statBlocked`, `statTodo` with:

```javascript
// Progress ring
const percent = p.percent;
const circumference = 251.2;
const offset = circumference - (circumference * percent / 100);
document.getElementById('ringProgress').style.strokeDashoffset = offset;
document.getElementById('ringPercent').textContent = percent + '%';
document.getElementById('statDone').textContent = p.completed;
document.getElementById('statProgress').textContent = p.in_progress;
document.getElementById('statBlocked').textContent = p.blocked;
document.getElementById('statTodo').textContent = p.not_started;

// Mini stats
document.getElementById('statNextActions').textContent = nextActions.next_actions ? nextActions.next_actions.length : 0;
document.getElementById('statBlockedCount').textContent = p.blocked;
document.getElementById('statTimeline').textContent = overview.outcome.timeline || '—';
```

- [ ] **Step 4: Update plan header markup**

Replace `<h2 id="planTitle">` and `<p id="planDescription">` with:

```html
<div class="plan-header" style="margin-bottom:28px;">
    <h2 id="planTitle" style="font-size:26px;font-weight:700;letter-spacing:-0.03em;margin-bottom:6px;"></h2>
    <div id="planMeta" style="display:flex;align-items:center;gap:16px;color:var(--text-secondary);font-size:13px;"></div>
</div>
```

Update `refreshPlanView()` to populate meta:

```javascript
document.getElementById('planTitle').textContent = overview.outcome.title;
document.getElementById('planMeta').innerHTML =
    `<span>${overview.total_steps} steps</span>` +
    `<span style="color:var(--text-muted)">·</span>` +
    `<span>${overview.outcome.timeline || 'No timeline'}</span>` +
    `<span style="color:var(--text-muted)">·</span>` +
    `<span style="color:var(--success)">${p.percent}% complete</span>`;
```

- [ ] **Step 5: Verify progress ring animates on plan load**

Run server, load a plan, confirm ring animates from 0 to the actual percentage.

- [ ] **Step 6: Commit**

```bash
git add http_server.py
git commit -m "feat: add animated SVG progress ring and mini stat cards"
```

---

## Chunk 2: Step Cards Redesign + Action Bar

Tasks 4–5 replace the step cards with the new design and add the filter/action bar.

### Task 4: Redesign Step Cards and Action Bar

**Files:**
- Modify: `http_server.py` — CSS for step cards, action bar, filter pills; HTML for action bar; JS for `refreshPlanView` step rendering

- [ ] **Step 1: Remove old step and button-group CSS, add new CSS**

Remove all CSS rules for: `.btn-group`, `.step-list`, `.step-item`, `.step-item:hover`, `.step-item.completed`, `.step-item.completed .step-header`, `.step-item.completed .step-desc`, `.step-item.completed:hover`, `.step-item.in_progress`, `.step-item.blocked`, `.step-header`, `.step-title`, `.step-badge`, `.badge-*`, `.step-desc`, `.step-actions`, `.step-actions button`, `.next-actions`, `.next-actions h3`, `.next-actions ul`, `.next-actions li`, `.section-label`.

Also remove the now-unused button styles: `.btn-success`, `.btn-accent`, `.btn-error`, `.btn-ghost`.

Add:

```css
/* Action bar */
.action-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.action-btn {
    padding: 8px 16px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--surface-1);
    color: var(--text-secondary);
    cursor: pointer;
    font-size: 13px;
    font-family: inherit;
    font-weight: 500;
    transition: all 150ms;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    line-height: 1;
}
.action-btn:hover { background: var(--surface-2); color: var(--text-primary); border-color: var(--border-hover); }
.action-btn:active { transform: scale(0.97); }
.action-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.action-btn.primary {
    background: var(--accent);
    border-color: var(--accent);
    color: white;
    box-shadow: 0 2px 8px var(--accent-glow);
}
.action-btn.primary:hover { background: var(--accent-light); }

.filter-pills {
    display: flex;
    gap: 2px;
    margin-left: auto;
    background: var(--surface-1);
    border-radius: var(--radius-sm);
    padding: 3px;
    border: 1px solid var(--border);
}
.filter-pill {
    padding: 5px 12px;
    border-radius: 6px;
    border: none;
    background: transparent;
    color: var(--text-muted);
    font-size: 12px;
    font-family: inherit;
    font-weight: 500;
    cursor: pointer;
    transition: all 150ms;
}
.filter-pill:hover { color: var(--text-secondary); }
.filter-pill.active { background: var(--surface-3); color: var(--text-primary); }

/* Step cards */
.step-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.step-card {
    background: var(--surface-1);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    transition: all 150ms;
    cursor: pointer;
}
.step-card:hover {
    background: var(--surface-2);
    border-color: var(--border-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.step-drag {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5px;
    color: var(--text-muted);
    cursor: grab;
    flex-shrink: 0;
    opacity: 0;
    transition: opacity 150ms;
    padding: 4px 2px;
}
.step-card:hover .step-drag { opacity: 1; }
.drag-dot {
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: currentColor;
}
.drag-row { display: flex; gap: 3px; }

.step-ring {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: 2px solid var(--text-muted);
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 150ms;
    cursor: pointer;
    font-size: 11px;
    font-weight: 700;
}
.step-ring:hover { border-color: var(--text-secondary); }
.step-ring.completed { border-color: var(--success); background: var(--success); color: white; }
.step-ring.in_progress { border-color: var(--accent); background: var(--accent-subtle); }
.step-ring.in_progress::after { content: ''; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
.step-ring.blocked { border-color: var(--error); background: rgba(248,113,113,0.1); color: var(--error); }

.step-body { flex: 1; min-width: 0; }
.step-card-title { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.step-card-desc {
    font-size: 12px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-top: 2px;
}

.step-card.completed .step-card-title { color: var(--text-secondary); text-decoration: line-through; text-decoration-color: var(--text-muted); }
.step-card.completed .step-card-desc { color: var(--text-muted); }

.step-priority {
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 500;
    flex-shrink: 0;
}
.step-priority.critical { background: rgba(248,113,113,0.1); color: var(--error); }
.step-priority.high { background: rgba(251,191,36,0.1); color: var(--warning); }
.step-priority.medium { background: rgba(124,92,252,0.1); color: var(--accent-light); }
.step-priority.low { background: rgba(136,136,160,0.1); color: var(--text-secondary); }

.step-hover-actions {
    display: flex;
    gap: 4px;
    opacity: 0;
    transition: opacity 150ms;
    flex-shrink: 0;
}
.step-card:hover .step-hover-actions { opacity: 1; }

.step-action-btn {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--surface-2);
    color: var(--text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    transition: all 150ms;
    font-family: inherit;
}
.step-action-btn:hover { background: var(--surface-3); color: var(--text-primary); }
.step-action-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
```

- [ ] **Step 2: Replace action bar HTML**

Remove the old `<div class="btn-group">` block and the `<div class="next-actions">` block and the `<div class="section-label">Steps</div>`. Replace with:

```html
<div class="action-bar">
    <button class="action-btn primary" onclick="showAddStepModal()">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
        Add Step
    </button>
    <button class="action-btn" onclick="generateAISteps()">AI Generate</button>
    <button class="action-btn" onclick="showExportMenu(event)">Export ▾</button>
    <div class="filter-pills" role="tablist">
        <button class="filter-pill active" role="tab" aria-selected="true" onclick="setFilter('all', this)">All</button>
        <button class="filter-pill" role="tab" aria-selected="false" onclick="setFilter('not_started', this)">To Do</button>
        <button class="filter-pill" role="tab" aria-selected="false" onclick="setFilter('in_progress', this)">Active</button>
        <button class="filter-pill" role="tab" aria-selected="false" onclick="setFilter('completed', this)">Done</button>
        <button class="filter-pill" role="tab" aria-selected="false" onclick="setFilter('blocked', this)">Blocked</button>
    </div>
</div>
<div class="step-list" id="stepList"></div>
```

- [ ] **Step 3: Rewrite step rendering in `refreshPlanView()`**

Replace the entire `// Steps` section of `refreshPlanView()` with:

```javascript
// Steps
const stepList = document.getElementById('stepList');
if (steps.steps && steps.steps.length > 0) {
    window._allSteps = steps.steps;
    renderSteps(steps.steps);
} else {
    stepList.innerHTML = '<div class="empty-state"><h2>No steps yet</h2><p>Click "Add Step" or "AI Generate" to get started</p></div>';
}
```

- [ ] **Step 4: Add `renderSteps()`, `setFilter()`, search filter functions**

Add to the `<script>` section:

```javascript
let currentFilter = 'all';
let searchQuery = '';
let expandedStepId = null;

function renderSteps(steps) {
    const stepList = document.getElementById('stepList');
    let filtered = steps;

    if (currentFilter !== 'all') {
        filtered = filtered.filter(s => s.status === currentFilter);
    }
    if (searchQuery) {
        const q = searchQuery.toLowerCase();
        filtered = filtered.filter(s =>
            s.title.toLowerCase().includes(q) ||
            (s.description && s.description.toLowerCase().includes(q))
        );
    }

    if (filtered.length === 0) {
        stepList.innerHTML = '<div class="empty-state"><p>No matching steps</p></div>';
        return;
    }

    stepList.innerHTML = filtered.map(s => {
        const ringClass = s.status !== 'not_started' ? s.status : '';
        const ringContent = s.status === 'completed' ? '✓' : s.status === 'blocked' ? '!' : '';
        return `
        <div class="step-card ${s.status}" draggable="true" data-step-id="${s.id}"
             ondragstart="onDragStart(event, ${s.id})" ondragover="onDragOver(event)" ondrop="onDrop(event, ${s.id})" ondragend="onDragEnd(event)"
             onclick="toggleExpand(${s.id}, event)">
            <div class="step-drag"><div class="drag-row"><span class="drag-dot"></span><span class="drag-dot"></span></div><div class="drag-row"><span class="drag-dot"></span><span class="drag-dot"></span></div><div class="drag-row"><span class="drag-dot"></span><span class="drag-dot"></span></div></div>
            <div class="step-ring ${ringClass}" onclick="cycleStatus(${s.id}, '${s.status}', event)" title="Click to change status">${ringContent}</div>
            <div class="step-body">
                <div class="step-card-title">#${s.id} ${s.title}</div>
                <div class="step-card-desc">${s.description || 'No description'}</div>
            </div>
            <span class="step-priority ${s.priority}">${s.priority}</span>
            <div class="step-hover-actions">
                <button class="step-action-btn" onclick="updateStatus(${s.id}, 'in_progress'); event.stopPropagation();" title="Start" aria-label="Start step ${s.id}">▶</button>
                <button class="step-action-btn" onclick="updateStatus(${s.id}, 'completed'); event.stopPropagation();" title="Done" aria-label="Complete step ${s.id}">✓</button>
                <button class="step-action-btn" onclick="updateStatus(${s.id}, 'blocked'); event.stopPropagation();" title="Block" aria-label="Block step ${s.id}">⚠</button>
            </div>
        </div>`;
    }).join('');
}

function setFilter(filter, el) {
    currentFilter = filter;
    document.querySelectorAll('.filter-pill').forEach(p => { p.classList.remove('active'); p.setAttribute('aria-selected', 'false'); });
    el.classList.add('active');
    el.setAttribute('aria-selected', 'true');
    if (window._allSteps) renderSteps(window._allSteps);
}

function cycleStatus(stepId, current, event) {
    event.stopPropagation();
    const cycle = { not_started: 'in_progress', in_progress: 'completed', completed: 'not_started', blocked: 'in_progress' };
    updateStatus(stepId, cycle[current] || 'in_progress');
}

// Search
document.getElementById('searchInput').addEventListener('input', function(e) {
    searchQuery = e.target.value;
    if (window._allSteps) renderSteps(window._allSteps);
});
```

- [ ] **Step 5: Add export dropdown**

Add CSS:

```css
.export-menu {
    position: fixed;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 4px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    z-index: 50;
    display: none;
}
.export-menu.open { display: block; }
.export-menu button {
    display: block;
    width: 100%;
    padding: 8px 16px;
    border: none;
    background: none;
    color: var(--text-secondary);
    font-size: 13px;
    font-family: inherit;
    text-align: left;
    cursor: pointer;
    border-radius: 4px;
    transition: all 150ms;
}
.export-menu button:hover { background: var(--surface-3); color: var(--text-primary); }
```

Add HTML (before closing `</div>` of `.main-scroll`):

```html
<div class="export-menu" id="exportMenu">
    <button onclick="exportPDF(); closeExportMenu()">PDF</button>
    <button onclick="exportHTML(); closeExportMenu()">HTML</button>
    <button onclick="exportICal(); closeExportMenu()">iCal</button>
</div>
```

Add JS:

```javascript
function showExportMenu(e) {
    const menu = document.getElementById('exportMenu');
    const rect = e.target.getBoundingClientRect();
    menu.style.top = (rect.bottom + 4) + 'px';
    menu.style.left = rect.left + 'px';
    menu.classList.toggle('open');
    e.stopPropagation();
}
function closeExportMenu() { document.getElementById('exportMenu').classList.remove('open'); }
document.addEventListener('click', closeExportMenu);
```

- [ ] **Step 6: Verify step cards render, filter works, search works**

Run server, load a plan, confirm:
- Step cards show with drag handles, status rings, priority badges
- Filter pills switch between All/To Do/Active/Done/Blocked
- Search narrows results as you type
- Clicking a status ring cycles its state

- [ ] **Step 7: Commit**

```bash
git add http_server.py
git commit -m "feat: redesign step cards with status rings, action bar, search and filter"
```

---

## Chunk 3: Interactive Features

Tasks 5–8 add expandable cards, drag-reorder, collapsible sidebar, keyboard shortcuts, theme toggle, and confetti.

### Task 5: Expandable Step Cards + Backend Detail Fields

**Files:**
- Modify: `http_server.py:113-145` — add `resources_needed` and `risks` to step detail response
- Modify: `http_server.py` — JS for expand/collapse

- [ ] **Step 1: Update `get_all_steps()` to include resources and risks**

In the `if include_details:` block (around line 131), add `resources_needed` and `risks`:

```python
if include_details:
    step_data.update({
        'description': step.description,
        'dependencies': step.dependencies,
        'duration': step.estimated_duration,
        'success_criteria': step.success_criteria,
        'resources_needed': [
            {'name': r.name, 'type': r.type, 'amount': r.amount}
            for r in step.resources_needed
        ] if step.resources_needed else [],
        'risks': [
            {'description': r.description, 'probability': r.probability, 'impact': r.impact, 'mitigation': r.mitigation}
            for r in step.risks
        ] if step.risks else [],
        'notes': step.notes
    })
```

- [ ] **Step 2: Add expanded card CSS**

```css
.step-expanded {
    background: var(--surface-1);
    border: 1px solid var(--accent);
    border-radius: var(--radius);
    padding: 20px;
    margin-bottom: 6px;
    box-shadow: 0 0 0 1px var(--accent-subtle), 0 8px 24px rgba(0,0,0,0.2);
    animation: expandIn 200ms ease;
}
@keyframes expandIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

.step-expanded-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}

.step-expanded-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}
@media (max-width: 600px) { .step-expanded-grid { grid-template-columns: 1fr; } }

.detail-section h4 {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.detail-section p, .detail-section li {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
}
.detail-section ul { list-style: none; padding: 0; margin: 0; }
.detail-section li::before { content: '→ '; color: var(--accent); }
.detail-empty { color: var(--text-muted); font-style: italic; font-size: 12px; }
```

- [ ] **Step 3: Add `toggleExpand()` function**

```javascript
function toggleExpand(stepId, event) {
    if (event.target.closest('.step-hover-actions') || event.target.closest('.step-ring') || event.target.closest('.step-drag')) return;

    if (expandedStepId === stepId) {
        expandedStepId = null;
    } else {
        expandedStepId = stepId;
    }
    if (window._allSteps) renderSteps(window._allSteps);
}
```

- [ ] **Step 4: Update `renderSteps()` to render expanded card inline**

In the `renderSteps()` function, after generating each step card HTML, check if the step is expanded. Replace the `.map()` callback to add the expanded panel after the card:

After the closing `</div>` of the step-card div, append:

```javascript
// Inside the .map() callback, after the step-card closing tag:
const expanded = (expandedStepId === s.id) ? `
<div class="step-expanded">
    <div class="step-expanded-header">
        <div class="step-ring ${ringClass}">${ringContent}</div>
        <div style="flex:1">
            <div class="step-card-title">#${s.id} ${s.title}</div>
        </div>
        <span class="step-priority ${s.priority}">${s.priority}</span>
        <div class="step-hover-actions" style="opacity:1">
            <button class="step-action-btn" onclick="updateStatus(${s.id}, 'in_progress'); event.stopPropagation();" title="Start">▶</button>
            <button class="step-action-btn" onclick="updateStatus(${s.id}, 'completed'); event.stopPropagation();" title="Done">✓</button>
            <button class="step-action-btn" onclick="updateStatus(${s.id}, 'blocked'); event.stopPropagation();" title="Block">⚠</button>
        </div>
    </div>
    <div class="step-expanded-grid">
        <div class="detail-section">
            <h4>Description</h4>
            <p>${s.description || '<span class="detail-empty">No description</span>'}</p>
        </div>
        <div class="detail-section">
            <h4>Dependencies</h4>
            ${s.dependencies && s.dependencies.length > 0
                ? '<ul>' + s.dependencies.map(d => '<li>Step #' + d + '</li>').join('') + '</ul>'
                : '<span class="detail-empty">None</span>'}
        </div>
        <div class="detail-section">
            <h4>Resources</h4>
            ${s.resources_needed && s.resources_needed.length > 0
                ? '<ul>' + s.resources_needed.map(r => '<li>' + r.name + (r.amount ? ' (' + r.amount + ')' : '') + '</li>').join('') + '</ul>'
                : '<span class="detail-empty">None listed</span>'}
        </div>
        <div class="detail-section">
            <h4>Risks</h4>
            ${s.risks && s.risks.length > 0
                ? '<ul>' + s.risks.map(r => '<li>' + r.description + ' <span style="color:var(--text-muted)">(' + r.probability + '/' + r.impact + ')</span></li>').join('') + '</ul>'
                : '<span class="detail-empty">None identified</span>'}
        </div>
    </div>
</div>` : '';

// Return step card + expanded panel
return stepCardHtml + expanded;
```

This means the full `.map()` return becomes the step card div string + the `expanded` string concatenated.

- [ ] **Step 5: Verify expand/collapse works**

Run server, load a plan, click a step card — it should expand with details below. Click again to collapse. Click another to swap which is expanded.

- [ ] **Step 6: Commit**

```bash
git add http_server.py
git commit -m "feat: add expandable step cards with detail panels"
```

---

### Task 6: Drag-to-Reorder Steps

**Files:**
- Modify: `http_server.py` — new `/api/plan/reorder` endpoint + JS drag handlers

- [ ] **Step 1: Add reorder endpoint**

Add after `update_step_status` (around line 250):

```python
@app.route('/api/plan/reorder', methods=['PUT'])
def reorder_step():
    """Reorder a step to a new position"""
    global current_plan
    if not current_plan:
        return jsonify({'status': 'error', 'message': 'No plan loaded'}), 400

    data = request.json
    step_id = data['step_id']
    new_position = data['new_position']

    # Find and remove the step
    step = None
    for i, s in enumerate(current_plan.steps):
        if s.id == step_id:
            step = current_plan.steps.pop(i)
            break

    if not step:
        return jsonify({'status': 'error', 'message': 'Step not found'}), 404

    # Insert at new position (clamped)
    new_position = max(0, min(new_position, len(current_plan.steps)))
    current_plan.steps.insert(new_position, step)

    return jsonify({'status': 'success', 'message': f'Step {step_id} moved to position {new_position}'})
```

- [ ] **Step 2: Add JS drag handlers**

The `draggable="true"`, `ondragstart`, `ondragover`, `ondrop`, `ondragend` attributes are already in the step card HTML from Task 4. Add the handler functions:

```javascript
let draggedStepId = null;

function onDragStart(e, stepId) {
    draggedStepId = stepId;
    e.dataTransfer.effectAllowed = 'move';
    e.target.style.opacity = '0.4';
}

function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    const card = e.target.closest('.step-card');
    if (card) {
        document.querySelectorAll('.step-card').forEach(c => c.style.borderTopColor = '');
        card.style.borderTopColor = 'var(--accent)';
    }
}

function onDrop(e, targetStepId) {
    e.preventDefault();
    document.querySelectorAll('.step-card').forEach(c => { c.style.borderTopColor = ''; c.style.opacity = ''; });
    if (draggedStepId === null || draggedStepId === targetStepId) return;

    const targetIndex = window._allSteps.findIndex(s => s.id === targetStepId);
    api('/api/plan/reorder', {
        method: 'PUT',
        body: JSON.stringify({ step_id: draggedStepId, new_position: targetIndex })
    }).then(() => {
        return api('/api/plan/save', { method: 'POST', body: JSON.stringify({ filename: currentPlan }) });
    }).then(() => {
        refreshPlanView();
    });
    draggedStepId = null;
}

function onDragEnd(e) {
    e.target.style.opacity = '';
    document.querySelectorAll('.step-card').forEach(c => c.style.borderTopColor = '');
    draggedStepId = null;
}
```

- [ ] **Step 3: Verify drag-reorder works**

Run server, load a plan with multiple steps, drag a step to a new position. Confirm it persists after page refresh.

- [ ] **Step 4: Commit**

```bash
git add http_server.py
git commit -m "feat: add drag-to-reorder steps with backend endpoint"
```

---

### Task 7: Collapsible Sidebar + Theme Toggle

**Files:**
- Modify: `http_server.py` — JS functions for sidebar toggle and theme toggle

- [ ] **Step 1: Add sidebar toggle JS**

```javascript
function toggleSidebar() {
    const layout = document.getElementById('appLayout');
    const collapsed = layout.classList.toggle('collapsed');
    localStorage.setItem('sidebar-collapsed', collapsed);
    document.querySelector('.collapse-btn').textContent = collapsed ? '▷' : '◁';
}

// Restore sidebar state on load
(function() {
    if (localStorage.getItem('sidebar-collapsed') === 'true') {
        document.getElementById('appLayout').classList.add('collapsed');
        document.querySelector('.collapse-btn').textContent = '▷';
    }
})();
```

- [ ] **Step 2: Add theme toggle JS**

```javascript
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateThemeIcon(next);
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    if (theme === 'light') {
        icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
    } else {
        icon.innerHTML = '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>';
    }
}

// Restore theme on load
(function() {
    const saved = localStorage.getItem('theme') || 'dark';
    if (saved === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        updateThemeIcon('light');
    }
})();
```

- [ ] **Step 3: Verify sidebar collapses and theme toggles**

Run server, click collapse button — sidebar shrinks to icons. Click theme toggle — switches to light mode. Refresh — both states persist.

- [ ] **Step 4: Commit**

```bash
git add http_server.py
git commit -m "feat: add collapsible sidebar and dark/light theme toggle"
```

---

### Task 8: Keyboard Shortcuts + Completion Confetti

**Files:**
- Modify: `http_server.py` — JS for keyboard handlers, shortcuts modal, confetti canvas

- [ ] **Step 1: Add shortcuts overlay CSS and HTML**

CSS:

```css
.shortcuts-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    z-index: 100;
    display: none;
    align-items: center;
    justify-content: center;
}
.shortcuts-overlay.active { display: flex; }

.shortcuts-card {
    background: var(--surface-1);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 28px;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 24px 48px rgba(0,0,0,0.4);
}
.shortcuts-card h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }

.shortcut-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
    color: var(--text-secondary);
}
.shortcut-row:last-child { border-bottom: none; }
.shortcut-row kbd {
    padding: 3px 8px;
    border-radius: 4px;
    background: var(--surface-3);
    border: 1px solid var(--border);
    font-size: 12px;
    font-family: inherit;
    color: var(--text-primary);
    min-width: 28px;
    text-align: center;
}

.shortcut-hint {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 8px 14px;
    border-radius: var(--radius-sm);
    background: var(--surface-2);
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    transition: all 150ms;
}
.shortcut-hint:hover { color: var(--text-secondary); border-color: var(--border-hover); }
.shortcut-hint kbd {
    padding: 2px 6px;
    border-radius: 4px;
    background: var(--surface-3);
    border: 1px solid var(--border);
    font-size: 11px;
    font-family: inherit;
}
```

HTML (add before closing `</body>`):

```html
<div class="shortcuts-overlay" id="shortcutsOverlay" onclick="if(event.target===this)hideShortcuts()">
    <div class="shortcuts-card">
        <h2>Keyboard Shortcuts</h2>
        <div class="shortcut-row"><span>New plan</span><kbd>n</kbd></div>
        <div class="shortcut-row"><span>Add step</span><kbd>s</kbd></div>
        <div class="shortcut-row"><span>Search</span><kbd>/</kbd></div>
        <div class="shortcut-row"><span>Navigate steps</span><kbd>j</kbd> <kbd>k</kbd></div>
        <div class="shortcut-row"><span>Start selected</span><kbd>1</kbd></div>
        <div class="shortcut-row"><span>Complete selected</span><kbd>2</kbd></div>
        <div class="shortcut-row"><span>Block selected</span><kbd>3</kbd></div>
        <div class="shortcut-row"><span>Close / Deselect</span><kbd>Esc</kbd></div>
        <div class="shortcut-row"><span>Show shortcuts</span><kbd>?</kbd></div>
    </div>
</div>
<div class="shortcut-hint" onclick="showShortcuts()"><kbd>?</kbd> Shortcuts</div>
<canvas id="confettiCanvas" style="position:fixed;inset:0;pointer-events:none;z-index:300;"></canvas>
```

- [ ] **Step 2: Add keyboard handler JS**

```javascript
let selectedStepIndex = -1;

function showShortcuts() { document.getElementById('shortcutsOverlay').classList.add('active'); }
function hideShortcuts() { document.getElementById('shortcutsOverlay').classList.remove('active'); }

document.addEventListener('keydown', function(e) {
    const tag = document.activeElement.tagName;
    const inInput = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
    const modalOpen = document.querySelector('.modal.active') || document.querySelector('.shortcuts-overlay.active');

    if (e.key === 'Escape') {
        if (document.querySelector('.shortcuts-overlay.active')) { hideShortcuts(); return; }
        if (document.querySelector('.modal.active')) { document.querySelectorAll('.modal.active').forEach(m => m.classList.remove('active')); return; }
        if (inInput) { document.activeElement.blur(); return; }
        if (expandedStepId !== null) { expandedStepId = null; if (window._allSteps) renderSteps(window._allSteps); return; }
        selectedStepIndex = -1;
        highlightSelected();
        return;
    }

    if (inInput || modalOpen) return;

    switch(e.key) {
        case 'n': showCreateModal(); e.preventDefault(); break;
        case 's': showAddStepModal(); e.preventDefault(); break;
        case '/': document.getElementById('searchInput').focus(); e.preventDefault(); break;
        case '?': showShortcuts(); e.preventDefault(); break;
        case 'j':
            if (window._allSteps && window._allSteps.length > 0) {
                selectedStepIndex = Math.min(selectedStepIndex + 1, window._allSteps.length - 1);
                highlightSelected();
            }
            e.preventDefault();
            break;
        case 'k':
            if (window._allSteps) {
                selectedStepIndex = Math.max(selectedStepIndex - 1, 0);
                highlightSelected();
            }
            e.preventDefault();
            break;
        case '1':
            if (selectedStepIndex >= 0 && window._allSteps[selectedStepIndex]) {
                updateStatus(window._allSteps[selectedStepIndex].id, 'in_progress');
            }
            break;
        case '2':
            if (selectedStepIndex >= 0 && window._allSteps[selectedStepIndex]) {
                updateStatus(window._allSteps[selectedStepIndex].id, 'completed');
            }
            break;
        case '3':
            if (selectedStepIndex >= 0 && window._allSteps[selectedStepIndex]) {
                updateStatus(window._allSteps[selectedStepIndex].id, 'blocked');
            }
            break;
    }
});

function highlightSelected() {
    document.querySelectorAll('.step-card').forEach((c, i) => {
        c.style.outline = i === selectedStepIndex ? '2px solid var(--accent)' : '';
        c.style.outlineOffset = i === selectedStepIndex ? '2px' : '';
        if (i === selectedStepIndex) c.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    });
}
```

- [ ] **Step 3: Add confetti JS**

```javascript
function fireConfetti(x, y, count) {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const canvas = document.getElementById('confettiCanvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');
    const colors = ['#7c5cfc', '#9b7dff', '#34d399', '#fbbf24', '#f87171'];
    const particles = [];

    for (let i = 0; i < count; i++) {
        particles.push({
            x: x, y: y,
            vx: (Math.random() - 0.5) * 12,
            vy: (Math.random() - 0.7) * 12,
            size: Math.random() * 6 + 3,
            color: colors[Math.floor(Math.random() * colors.length)],
            life: 1,
            rotation: Math.random() * 360
        });
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let alive = false;
        particles.forEach(p => {
            if (p.life <= 0) return;
            alive = true;
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.3;
            p.life -= 0.015;
            p.rotation += p.vx * 2;
            ctx.save();
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation * Math.PI / 180);
            ctx.globalAlpha = p.life;
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
            ctx.restore();
        });
        if (alive) requestAnimationFrame(animate);
        else ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    requestAnimationFrame(animate);
}
```

- [ ] **Step 4: Wire confetti into `updateStatus()`**

Update `updateStatus()` to fire confetti when marking done:

```javascript
async function updateStatus(stepId, status) {
    await api('/api/plan/step/' + stepId + '/status', {
        method: 'PUT',
        body: JSON.stringify({ status })
    });
    await api('/api/plan/save', { method: 'POST', body: JSON.stringify({ filename: currentPlan }) });

    if (status === 'completed') {
        // Find the step card element for position
        const card = document.querySelector(`[data-step-id="${stepId}"]`);
        if (card) {
            const rect = card.getBoundingClientRect();
            fireConfetti(rect.left + 30, rect.top + rect.height / 2, 25);
        }

        // Check if plan is 100% complete
        const overview = await api('/api/plan/overview');
        if (overview.progress && overview.progress.percent === 100) {
            setTimeout(() => {
                fireConfetti(window.innerWidth / 2, window.innerHeight / 2, 120);
                toast('All steps complete! 🎉');
            }, 400);
        }
    }

    toast('Status updated');
    refreshPlanView();
}
```

- [ ] **Step 5: Update modal CSS to use `.modal` class for consistency**

Ensure existing modals still work — the `.modal` and `.modal-content` CSS from before should be kept (update to use new tokens if needed). Also update the toast styles to use the new tokens. Keep the existing toast CSS but ensure `.toast` uses `var(--surface-2)` for background.

- [ ] **Step 6: Verify all features work end-to-end**

Run server, verify:
- Press `?` — shortcuts overlay appears
- Press `n` — new plan modal opens
- Press `/` — search box focuses
- Press `j`/`k` — step cards highlight
- Press `2` on selected step — marks complete + confetti
- Sun/moon toggles theme
- Sidebar collapses
- Drag a step to reorder
- Click step to expand

- [ ] **Step 7: Commit**

```bash
git add http_server.py
git commit -m "feat: add keyboard shortcuts, shortcuts overlay, and completion confetti"
```

---

## Chunk 4: Polish Pass

### Task 9: Final Polish — Empty States, Toasts, Focus Rings, Accessibility

**Files:**
- Modify: `http_server.py` — CSS tweaks, aria attributes, reduced-motion support

- [ ] **Step 1: Add focus-visible and reduced-motion CSS**

```css
/* Focus rings */
.plan-item:focus-visible,
.new-plan-btn:focus-visible,
.collapse-btn:focus-visible,
.action-btn:focus-visible,
.filter-pill:focus-visible,
.modal-close:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
    .ring-progress { transition: none; }
}
```

- [ ] **Step 2: Update empty state styling**

```css
.empty-state {
    text-align: center;
    padding: 64px 24px;
    color: var(--text-muted);
}
.empty-state h2 {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}
.empty-state p {
    font-size: 14px;
    color: var(--text-muted);
    max-width: 300px;
    margin: 0 auto;
}
```

- [ ] **Step 3: Update toast styling to match new design**

```css
.toast {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    padding: 10px 20px;
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-weight: 500;
    font-size: 13px;
    z-index: 200;
    animation: toastIn 200ms ease;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    background: var(--surface-2);
    border: 1px solid var(--border);
}
.toast::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
}
.toast-success::before { background: var(--success); box-shadow: 0 0 6px var(--success); }
.toast-error::before { background: var(--error); box-shadow: 0 0 6px var(--error); }

@keyframes toastIn {
    from { transform: translateX(-50%) translateY(12px); opacity: 0; }
    to { transform: translateX(-50%) translateY(0); opacity: 1; }
}
```

- [ ] **Step 4: Add `role` and `aria` attributes to key elements**

In the HTML:
- Add `role="navigation"` to `<aside class="sidebar">`
- Add `role="main"` to `<div class="main-scroll">`
- Add `aria-label="Plan list"` to `<ul class="plan-list">`
- Add `role="search"` to the search-box container div

- [ ] **Step 5: Final visual test**

Run server, test in both dark and light themes:
- All text is readable
- Focus rings visible when tabbing
- Toasts appear and auto-dismiss
- Empty states look good with no plan loaded
- Reduced motion: disable animations in browser prefs, verify no animations play

- [ ] **Step 6: Commit**

```bash
git add http_server.py
git commit -m "style: polish pass — focus rings, a11y, reduced motion, toast/empty state updates"
```

---

## Summary

| Chunk | Tasks | What It Delivers |
|-------|-------|-----------------|
| 1 | 1–3 | New design system, layout with sidebar + header, progress ring + mini stats |
| 2 | 4 | Redesigned step cards, action bar, search/filter |
| 3 | 5–8 | Expandable cards, drag-reorder, collapsible sidebar, theme toggle, keyboard shortcuts, confetti |
| 4 | 9 | Accessibility, focus rings, reduced motion, toast/empty state polish |

**Total:** 9 tasks, ~40 steps. One backend change (reorder endpoint). Everything else is CSS/HTML/JS in the embedded SPA.
