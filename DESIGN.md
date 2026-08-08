---
version: alpha
name: Sim, Aceito! Prestige
description: Visual identity and design system tokens for Wedding Management System (Eye-friendly UI for wedding planners)
colors:
  primary: "#7C3AED"
  primary-hover: "#6D28D9"
  secondary: "#F5F3FF"
  surface: "#FAFAFB"
  surface-dark: "#09090B"
  surface-dark-secondary: "#18181B"
  text-primary: "#1A1C1E"
  text-secondary: "#52585E"
  text-on-dark: "#FAFAFB"
  success: "#E0F2F1"
  success-text: "#004D40"
  warning: "#FEF3C7"
  warning-text: "#78350F"
  destructive: "#DC2626"
  destructive-subtle: "#FFE4E6"
  destructive-text: "#881337"
  info: "#E0F2FE"
  info-text: "#075985"
  white: "#FFFFFF"
typography:
  h1:
    fontFamily: Plus Jakarta Sans Variable
    fontSize: 32px
    fontWeight: 700
    lineHeight: 1.2
  h2:
    fontFamily: Plus Jakarta Sans Variable
    fontSize: 24px
    fontWeight: 600
    lineHeight: 1.3
  body-md:
    fontFamily: IBM Plex Sans Variable
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  label-mono:
    fontFamily: JetBrains Mono Variable
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.4
rounded:
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
spacing:
  base: 16px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: 12px
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-destructive:
    backgroundColor: "{colors.destructive}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: 12px
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: 24px
  card-secondary:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.md}"
    padding: 16px
  card-dark:
    backgroundColor: "{colors.surface-dark-secondary}"
    textColor: "{colors.text-on-dark}"
    rounded: "{rounded.lg}"
    padding: 24px
  badge-success:
    backgroundColor: "{colors.success}"
    textColor: "{colors.success-text}"
    rounded: "{rounded.full}"
  badge-warning:
    backgroundColor: "{colors.warning}"
    textColor: "{colors.warning-text}"
    rounded: "{rounded.full}"
  badge-destructive:
    backgroundColor: "{colors.destructive-subtle}"
    textColor: "{colors.destructive-text}"
    rounded: "{rounded.full}"
  badge-info:
    backgroundColor: "{colors.info}"
    textColor: "{colors.info-text}"
    rounded: "{rounded.full}"
  dialog:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
  sheet:
    backgroundColor: "{colors.surface-dark}"
    textColor: "{colors.text-on-dark}"
    rounded: "{rounded.sm}"
---

# DESIGN.md — Sim, Aceito! Design System

Official design specification and design tokens for **Sim, Aceito!** (Wedding Management System).

---

## Overview

The visual identity is designed for professional wedding planners who use the platform **6 to 10 hours daily**. The design prioritizes visual elegance, high-contrast readability, soft rounded shapes, and eye-fatigue reduction.

- **Brand Tone:** Refined, calm, sophisticated (Violet Aura accent).
- **Ergonomics:** Eye-friendly tinted light backgrounds (`#FAFAFB` / `#F5F3FF`) instead of harsh pure whites.
- **Typography Strategy:** High-density data legibility using `Plus Jakarta Sans` for headers, `IBM Plex Sans` for UI prose, and `JetBrains Mono` for financial tables.

Detailed architectural rationale is documented in [design-system-rationale.md](docs/4-explanation/architecture/design-system-rationale.md).

---

## Colors

The color system features high-contrast neutrals anchored by a vibrant Violet Aura primary accent.

- **Primary (`#7C3AED` / `primary`):** Violet accent used for main interactive elements, primary buttons, and active states.
- **Secondary (`#F5F3FF` / `secondary`):** Soft violet tint used for highlighted panel backgrounds and active navigation items.
- **Surface (`#FAFAFB` / `surface`):** Eye-friendly off-white background for light mode pages.
- **Surface Dark (`#09090B` / `surface-dark`):** Dark mode background paired with `#18181B` card containers.
- **Success (`#E0F2F1` / `success`):** Pastel teal background with `#004D40` dark text for `PAID` / `SETTLED` badges.
- **Warning (`#FEF3C7` / `warning`):** Pastel yellow background with `#78350F` amber text for `PENDING` / `WARNING` alerts.
- **Destructive (`#DC2626` / `destructive`):** Vibrant red accent for critical buttons. Subtly tinted `#FFE4E6` background with `#881337` text for `OVERDUE` badges.

---

## Typography

Typography leverages three variable font families tailored for readability across dense tables and form layouts:

- **Headlines (`Plus Jakarta Sans Variable`):** Semi-Bold to Bold for section headers and modal titles.
- **Body (`IBM Plex Sans Variable`):** Regular 16px for form labels, prose, and navigation items.
- **Monospace (`JetBrains Mono Variable`):** Medium 14px for monetary amounts (BRL), dates, and timestamps.

---

## Layout

The layout uses a fluid grid for mobile viewports and a fixed max-width grid (1200px) for desktop dashboards.

- **Spacing Scale:** Strict 8px grid scale (`4px`, `8px`, `16px`, `24px`, `32px`).
- **Containment:** Related items are grouped into cards with 24px internal padding.
- **Negative Space:** Generous section spacing (`p-6` or `p-8`) to prevent cognitive clutter.

---

## Elevation & Depth

Depth is achieved through **Tonal Layering** and soft subtle shadows (`shadow-soft`) rather than heavy dark drop shadows.

- Cards sit on pure white (`#FFFFFF`) or `#18181B` surface panels over the tinted background.
- Overlays use smooth backdrop filters (`backdrop-blur-sm`).

---

## Shapes

All interactive containers, inputs, and cards use rounded corners:

- **Buttons & Inputs (`rounded-md`):** 8px corner radius.
- **Cards & Modals (`rounded-lg` / `rounded-xl`):** 12px corner radius.
- **Badges (`rounded-full`):** 9999px pill radius.

---

## Components

Guidance for core UI component atoms built with shadcn/ui + Tailwind CSS v4:

- **Dialog vs Sheet:**
  - **Dialog (Center Modal):** Used for quick confirmation alerts, security checks, or small forms (< 5 fields). Max size `sm` to `md`.
  - **Sheet (Side Drawer):** Used for rich entity details (`ExpenseDetailSheet`, contracts) with full-height vertical scroll.
- **Dashboard KPI Cards:** Display monetary total (mono font), pending item count badge, and quick-action link ("Ver"). Cards apply red/amber border states when urgent items > 0.
- **Toasts (Sonner):** Displayed in bottom-right corner with 150ms slide-in animation.
- **Loading States:** Shimmer skeleton placeholders during data fetching.

---

## Do's and Don'ts

- **Do** compose shadcn/ui components using Tailwind classes in feature components.
- **Don't** edit base UI files directly in `src/components/ui/`.
- **Do** use `JetBrains Mono` for all currency (BRL) and date formatting.
- **Don't** use inline CSS (`style={{}}`); use Tailwind utility classes.
- **Do** maintain WCAG AA contrast ratios across light and dark themes.
- **Don't** mix sharp 0px corners with rounded elements in the same container.
