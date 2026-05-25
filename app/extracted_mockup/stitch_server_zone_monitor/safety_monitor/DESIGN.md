---
name: Safety Monitor
colors:
  surface: '#fcf8fa'
  surface-dim: '#dcd9db'
  surface-bright: '#fcf8fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f5'
  surface-container: '#f0edef'
  surface-container-high: '#eae7e9'
  surface-container-highest: '#e4e2e4'
  on-surface: '#1b1b1d'
  on-surface-variant: '#45464d'
  inverse-surface: '#303032'
  inverse-on-surface: '#f3f0f2'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#505f76'
  on-secondary: '#ffffff'
  secondary-container: '#d0e1fb'
  on-secondary-container: '#54647a'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#271901'
  on-tertiary-container: '#98805d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#fcdeb5'
  tertiary-fixed-dim: '#dec29a'
  on-tertiary-fixed: '#271901'
  on-tertiary-fixed-variant: '#574425'
  background: '#fcf8fa'
  on-background: '#1b1b1d'
  surface-variant: '#e4e2e4'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  container-margin: 16px
  gutter: 16px
---

## Brand & Style
The design system is centered on **Modern Utility**. It balances the urgency of fire and smoke monitoring with a calm, professional aesthetic suitable for a high-fidelity graduation project. The visual language emphasizes clarity, speed of recognition, and reliability.

The style is **Modern/Minimalist** with a focus on information density that doesn't feel cluttered. It leverages high-contrast typography against a pristine light backdrop to ensure that critical safety data is legible at a glance, even in high-stress situations. The UI avoids unnecessary decorative elements, favoring structural integrity and functional depth.

## Colors
This design system utilizes a high-contrast palette to differentiate between administrative UI and live monitoring data.

- **Primary & Neutral:** A deep navy (#0F172A) is used for titles and primary branding to provide a grounded, authoritative feel. Secondary text uses a cool slate gray (#64748B) to maintain hierarchy without competing for attention.
- **Status Colors:** These are the core of the application. 
    - **Success (Green):** Indicates active monitoring and safe levels.
    - **Warning (Amber):** Indicates data gaps, sensor loading, or "No Data" states.
    - **Error (Red):** Reserved for disconnected hardware or critical fire/smoke alerts.
- **Backgrounds:** Pure white is used for the main canvas, with a very subtle off-white/gray (#F8FAFC) used for section grouping or secondary containers.

## Typography
The design system relies exclusively on **Inter** to provide a systematic, utilitarian feel that mirrors modern Android OS aesthetics. 

- **Hierarchy:** Headlines use a semi-bold to bold weight with slight negative letter-spacing to feel "tight" and professional. 
- **Body:** Standard body text is optimized for readability at 14px and 16px. 
- **Labels:** Micro-copy and status labels use an uppercase treatment with increased letter-spacing to distinguish them from interactive body text.
- **Contextual Scaling:** On mobile devices, the `headline-lg` scales down to 28px to prevent awkward line breaks while maintaining its visual impact.

## Layout & Spacing
The layout follows an **8dp grid system**, consistent with Material Design standards. 

- **Grid Model:** A 4-column fluid grid is used for mobile portrait view. On larger devices (tablets), this expands to an 8-column grid.
- **Margins:** Standard screen margins are set to 16px (md) to ensure content does not hug the bezel.
- **Rhythm:** Vertical spacing between cards and monitoring modules should strictly follow the 16px or 24px increments to maintain a structured, rhythmic flow.
- **Reflow:** For a monitoring app, layout should prioritize "Top-Down" hierarchy, where the most critical status (Active Fire or Disconnected Sensor) is pinned to the top of the viewport.

## Elevation & Depth
Depth is used sparingly and purposefully to indicate interactivity and importance.

- **Ambient Shadows:** Monitoring cards use a soft, diffused shadow (Blur: 12px, Y-Offset: 4px, Opacity: 6% Black) to lift them off the background without appearing heavy.
- **Tonal Layers:** Secondary information, such as "Sensor History" or "Logs," uses flat containers with subtle 1px strokes (#E2E8F0) instead of shadows to remain lower in the visual hierarchy.
- **Active States:** When a card is alerted (Error state), the elevation may increase slightly, or a high-contrast border in the status color (#EF4444) is added to provide immediate visual feedback.

## Shapes
The shape language is **Rounded**, conveying a modern, approachable, and high-fidelity "app-like" feel.

- **Base Radius:** Standard UI elements (inputs, small chips) use an 8px (0.5rem) radius.
- **Large Radius:** Primary monitoring cards and image containers use a 16px (1rem) radius to create a distinct containerized look.
- **Full Radius:** Status indicators and specific action buttons use a pill-shaped (full) radius to differentiate them from the structural rectangular cards.

## Components

- **Monitoring Cards:** These are the primary building blocks. They feature a 16px rounded corner, a soft ambient shadow, and a prominent image container at the top or side. The title is placed in the top-left, with the status badge in the top-right.
- **Status Badges (Chips):** Pill-shaped elements with a light tinted background and dark foreground text (e.g., Success Green text on a 10% opacity Green background).
- **Image Containers:** Use a subtle inner border or "placeholder" shimmer (Skeleton) for loading states. Images should be clipped to the container's 16px border radius.
- **Primary Buttons:** High-contrast navy (#0F172A) with white text, using an 8px radius. 
- **Input Fields:** Minimalist style with a 1px border (#CBD5E1), 8px radius, and clear focus states using the Primary Navy color.
- **Alert Banner:** A full-width, non-rounded component that sticks to the top of the screen during "Error" (Fire detected) states, using the Solid Error Red background with white text.
- **Lists:** Clean, horizontal dividers (1px) with 16px padding between items for sensor logs and history.