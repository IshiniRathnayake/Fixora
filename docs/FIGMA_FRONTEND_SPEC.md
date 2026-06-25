# Fixora — Figma Frontend Specification

**Student ID:** 2521838 | **Section 4.4 wireframes** | Design before React implementation

---

## 1. Figma file setup

| Setting | Value |
|---------|--------|
| File name | `Fixora-Dashboard-v1` |
| Frame (desktop) | **1440 × 900** (primary) |
| Frame (tablet) | 1024 × 768 (optional) |
| Grid | 8px base, 12 columns, margin 80px |
| Layout grid | 8px soft grid for spacing |

### Pages (Figma tabs)

1. **Cover** — project title, ID, date  
2. **Design system** — colours, type, components  
3. **Wireframes** — low-fidelity (optional)  
4. **Screens** — high-fidelity (this spec)  
5. **Prototype** — links between screens  

---

## 2. Design tokens (create as Figma variables)

### Colour

| Token | Hex | Use |
|-------|-----|-----|
| `bg/primary` | `#0B0F14` | App background |
| `bg/surface` | `#121820` | Cards, sidebar |
| `bg/elevated` | `#1A2330` | Hover, inputs |
| `border/default` | `#2A3544` | Dividers |
| `text/primary` | `#E8EDF4` | Headings, body |
| `text/muted` | `#8B9BB0` | Subtitles, labels |
| `brand/accent` | `#3D9CF5` | Logo, primary CTA |
| `brand/accent-pressed` | `#2563A8` | Button hover |
| `status/success` | `#34C759` | Healthy, resolved |
| `status/warning` | `#F5A623` | Medium alerts |
| `status/danger` | `#FF5C5C` | Critical, errors |
| `agent/monitoring` | `#82B366` | Agent chips |
| `agent/analysis` | `#9673A6` | Agent chips |
| `agent/data` | `#D6B656` | Agent chips |

### Typography (DM Sans + JetBrains Mono)

| Style | Font | Size | Weight | Line height |
|-------|------|------|--------|-------------|
| `H1/Page` | DM Sans | 28px | 600 | 120% |
| `H2/Section` | DM Sans | 18px | 600 | 130% |
| `Body` | DM Sans | 14px | 400 | 150% |
| `Caption` | DM Sans | 12px | 400 | 140% |
| `Label/UPPER` | DM Sans | 11px | 600 | 100%, letter-spacing 0.06em |
| `Code/SQL` | JetBrains Mono | 13px | 400 | 150% |

### Radius & spacing

- Radius: `8` (buttons), `12` (cards)  
- Spacing scale: 4, 8, 12, 16, 24, 32, 48  

---

## 3. Components (Figma component set)

Build as **variants** where noted.

| Component | Variants | Notes |
|-----------|----------|-------|
| `Button/Primary` | default, hover, disabled | Height 40px |
| `Button/Secondary` | default, hover | Outline `border/default` |
| `Input/Text` | default, focus, error | Height 44px |
| `Textarea/Query` | default, focus | Min-height 120px |
| `Card/Metric` | — | Label + large number |
| `Card/Panel` | — | Section container |
| `Badge/Severity` | critical, high, medium, low | Pill 24px height |
| `Badge/Agent` | monitoring, analysis, data | |
| `Nav/SidebarItem` | default, active | 240px sidebar |
| `Table/Row` | default, anomaly-highlight | |
| `Alert/Inline` | info, success, diagnostic | |
| `Avatar/User` | admin, viewer | Initials |

---

## 4. App shell (all authenticated screens)

```
┌──────────────────────────────────────────────────────────────┐
│ SIDEBAR 240px          │ MAIN (fill)                         │
│ Fixora logo            │ Page title + subtitle               │
│ ─────────────────      │ [optional action buttons]           │
│ ● Dashboard            │ Content cards / tables              │
│   Alerts               │                                     │
│   Logs                 │                                     │
│   Ask Fixora           │                                     │
│   Diagnostics          │                                     │
│   Enterprise           │                                     │
│   Settings (admin)     │                                     │
│ ─────────────────      │                                     │
│ [User name]            │                                     │
│ Administrator          │                                     │
│ [Sign out]             │                                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Screen specifications

### 5.1 Login (1440×900, centred card 400px)

- Logo: **Fix**ora (`ora` in accent)  
- Subtitle: *Enterprise AI administration*  
- Fields: Email, Password  
- Primary button: **Sign in**  
- Footer hint: *Demo: admin@fixora.local*  

**Reference HTML:** `design/figma-wireframes/01-login.html`

---

### 5.2 Dashboard — FR4 (main content)

**Header:** System health | subtitle | `Refresh` (secondary)

**Row 1 — 4 metric cards (equal width, gap 16)**

| Card | Label | Example value |
|------|-------|----------------|
| 1 | HEALTH SCORE | 84 |
| 2 | OPEN ALERTS | 3 |
| 3 | ANOMALIES (24H) | 7 |
| 4 | AVG QUERY LATENCY | 420ms |

**Row 2 — Recent diagnostics (panel)**  
- Title: Recent diagnostics  
- Item: **Root cause** bold + explanation muted + optional “Fix: …”  
- Empty: *No diagnostics yet. Run analysis from Logs.*

**Row 3 — two columns (60/40)**  
- Left: Recent alerts (list with severity badges)  
- Right: Agent activity (table: Agent | Status | Duration)

**Reference:** `02-dashboard.html`

---

### 5.3 Log monitoring — FR1

**Header:** Log monitoring  
**Actions:** `Load sample logs` (secondary) · `Run AI analysis` (primary)  

**Diagnostic banner** (conditional, accent border):  
- Root cause, explanation, suggested fix  

**Table columns:** Time | Level | Message | Anomaly  
- Anomaly rows: light red background `#FF5C5C` @ 8% opacity  

**Reference:** `03-logs.html`

---

### 5.4 Alerts — FR1

**Table:** Severity | Title | Summary | Status | Detected | Action  
- Severity: badge  
- Action (admin): **Ack** button  

**Reference:** `04-alerts.html`

---

### 5.5 Ask Fixora — FR3 (+ full diagnostic FR2)

**Mode toggle:** ◉ Full diagnostic (logs + NL) · ○ Data query only  

**Large textarea** with placeholder: *Ask in plain English…*  

**Chip suggestions (4):**  
- What caused the database slowdown…  
- Show me all failed orders  
- List inventory with zero quantity  

**Primary:** Run full diagnostic  

**Sections below (stacked panels):**  
1. AI diagnosis (root cause, remediation, pipeline ms)  
2. Generated SQL (mono block)  
3. Results table  

**Reference:** `05-query.html`

---

### 5.6 Diagnostics — FR2

**List of diagnostic cards**, each:  
- Root cause (H2) + confidence badge  
- Explanation  
- Remediation box (elevated bg)  
- Timestamp caption  

**Reference:** `06-diagnostics.html`

---

### 5.7 Enterprise (sample app)

**Table:** Ref | Customer | Status | Amount | Process (admin)  
**Status pills:** completed (green), processing (blue), failed (red)  

**Reference:** `07-enterprise.html`

---

### 5.8 Settings / RBAC — FR5 (admin only)

**Sections:**  
- Profile (read-only name, email)  
- Role: Administrator / Viewer (display)  
- User management table (optional prototype): Email | Role | Active  

**Reference:** `08-settings.html`

---

## 6. Import into Figma (fastest path)

### Option A — HTML wireframes (recommended)

1. Open `design/figma-wireframes/01-login.html` in Chrome (full screen).  
2. Install Figma plugin **「html.to.design」** or **「Wireframe Designer」**.  
3. Import URL or paste HTML → generates editable frames.  
4. Repeat per screen; align to 1440×900.  
5. Replace with **design tokens** from Section 2.

### Option B — Manual

1. Create frame 1440×900 per screen.  
2. Copy layout from Section 5 + open HTML references side-by-side.  
3. Build components from Section 3 first, then compose screens.

### Option C — Screenshot trace

1. Screenshot each HTML page at 1440px width.  
2. Place in Figma as reference layer (50% opacity).  
3. Trace with shapes + auto-layout.

---

## 7. Prototype flows (link in Figma)

| From | Action | To |
|------|--------|-----|
| Login | Sign in | Dashboard |
| Dashboard | Nav → Logs | Logs |
| Logs | Run analysis | Logs (diagnostic banner shown) |
| Dashboard | Nav → Ask Fixora | Query |
| Query | Run diagnostic | Query (results state) |
| Any | Sign out | Login |

---

## 8. After Figma → React

1. Export icons/assets as SVG if any.  
2. Document spacing in this file or Figma Dev Mode.  
3. Update `frontend/src/styles/global.css` tokens to match Figma variables.  
4. Refactor pages to match components 1:1.

---

## 9. Thesis figure captions

- *Figure X: Fixora dashboard wireframe (high-fidelity prototype, FR4).*  
- *Figure X: Natural language query interface wireframe (FR3).*  
- *Figure X: Role-based administration settings wireframe (FR5).*

**Source:** Researcher's own design, 2026.
