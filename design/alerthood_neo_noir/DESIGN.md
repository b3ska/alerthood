# Design System Specification: Editorial Neo-Brutalism

## 1. Overview & Creative North Star
**Creative North Star: "The Authoritative Signal"**

This design system rejects the "polite" and muted aesthetics of standard SaaS. For a neighborhood threat monitoring application, the UI must command attention without causing panic. We achieve this through **Editorial Neo-Brutalism**: a high-contrast, structural approach that combines the raw urgency of a broadsheet newspaper with the digital precision of a modern command center.

The "template" look is broken through **intentional asymmetry** and **high-scale typography**. Elements do not just sit on a grid; they "impact" the canvas. We use thick, unyielding strokes to contain critical information, ensuring that in a high-stress monitoring environment, the user’s eye is never lost in a sea of soft gradients.

---

## 2. Colors & Surface Architecture
The color palette is built on "Alert-First" logic. While the background remains a deep, obsidian charcoal, the semantic colors serve as high-frequency signals.

### Core Palette
- **Surface (Background):** `#131313` (Deep Charcoal)
- **Primary (Crime):** `#FFB4AA` / Primary Container: `#FF5545` (The "Vibrant Red" signal)
- **Secondary (Infrastructure):** `#FFBC7C` / Secondary Container: `#FE9400` (The "Bright Orange" utility)
- **Tertiary (Disaster):** `#E8B3FF` / Tertiary Container: `#C567F4` (The "Electric Purple" disturbance)
- **Success (Relevant):** Neon Green (Accent for validated intel)

### The "No-Line" Hierarchy Rule
In this system, we prohibit the use of 1px grey dividers for sectioning. Structural separation is achieved via:
1.  **Background Shifts:** Move from `surface` to `surface_container_low` to define different content zones.
2.  **The Structural Stroke:** When a boundary is required, it must be an intentional **2px or 3px solid black (#000000)** stroke. Anything thinner is considered a "design error."

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked, physical plates.
- **Base Layer:** `surface` (#131313)
- **Component Layer:** `surface_container` (#201F1F) with a `3px` solid black border.
- **Elevated Interactive Layer:** `surface_container_high` (#2A2A2A) with a **Hard Shadow** (`4px 4px 0px #000000`).

---

## 3. Typography
The typography is designed to feel like a modern headline. We utilize **Space Grotesk** for its aggressive, geometric personality in displays and **Inter** for its neutral, high-legibility performance in data-heavy body sections.

### Typography Scale
- **Display (Space Grotesk):** `3.5rem` / Bold. Used for critical counts (e.g., "12 ACTIVE ALERTS").
- **Headline (Space Grotesk):** `2rem` / Bold. Used for category headers.
- **Title (Inter):** `1.125rem` / Semi-Bold. Used for alert titles within cards.
- **Body (Inter):** `0.875rem` / Regular. Optimized for rapid scanning of threat descriptions.
- **Label (Inter):** `0.75rem` / Bold All-Caps. Used for metadata and timestamps.

---

## 4. Elevation & Impact (Depth)
Unlike traditional "Soft UI," we do not use blurs to convey depth. We use **Physical Offset**.

- **The Hard Shadow:** Interactive elements (cards, buttons) must use a non-blurred shadow. 
  - *Token:* `4px 4px 0px #000000`.
- **The "Ghost Border" Fallback:** For secondary information that requires containment but shouldn't compete with primary alerts, use the `outline_variant` at 20% opacity. 
- **Intentional Overlap:** To break the "web template" feel, allow high-priority badges (e.g., "CRITICAL") to physically overlap the border of their parent container by `-8px` on the Y-axis.

---

## 5. Components

### Mobile-First Threat Cards
Cards are the heartbeat of the system. 
- **Style:** `surface_container` background, `3px` black border, `md` (0.75rem) corner radius.
- **Layout:** No dividers. Use **Spacing 4** (1rem) to separate the Title from the Body. 
- **Visual Signal:** A vertical "Impact Bar" on the left edge using the semantic color (Red/Orange/Purple) at `6px` width.

### High-Impact Buttons
- **Primary:** `primary_container` (#FF5545) background, `3px` black border, `2px` black hard shadow. Text must be `on_primary_container`.
- **States:** On `:hover` or `:active`, the hard shadow disappears (0px offset), mimicking the physical act of "pressing" the button into the page.

### Category Badges (Chips)
- **Style:** High-contrast fills. Use semantic containers (e.g., `error_container` for Crime).
- **Typography:** `label-md` (Bold).
- **Radius:** `full` (9999px) to contrast against the `md` radius of the cards.

### Input Fields
- **Style:** `surface_container_lowest` (#0E0E0E) background.
- **Border:** `2px` solid `outline`. On focus, transition to `3px` solid `primary` with no transition timing (instant response).

---

## 6. Do’s and Don’ts

### Do
- **Do** use asymmetrical spacing. A card can have 24px padding on the left and 16px on the right to create a "brutalist" editorial feel.
- **Do** use the `12` (3rem) spacing token between major sections to allow the heavy borders room to breathe.
- **Do** use "Neon Green" exclusively for user-verified "True" actions to create a distinct psychological "Safe Zone."

### Don't
- **Don't** use soft drop shadows. If it’s not a hard, 0-blur offset, it doesn't belong in this system.
- **Don't** use 1px lines. They disappear on high-density mobile screens and weaken the brand’s "Authoritative" voice.
- **Don't** use "Grey" for text on semantic backgrounds. Use the designated `on_` tokens (e.g., `on_primary_container`) to ensure AAA accessibility.
- **Don't** use subtle animations. Transitions should be "Snappy" (0.1s or 0s) to reflect the urgency of the data.