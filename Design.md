# Design System — Editorial / Minimal Product UI

## 1. Design Direction

The product should feel **editorial, premium, minimal, confident, and slightly experimental**.

The visual language is inspired by the two supplied references:

- Strong vertical/editorial typography
- Large areas of solid color
- High contrast
- Restrained use of imagery
- Large whitespace
- Clean geometric cards
- Serif italic used as an expressive accent against a modern sans-serif
- A fashion/editorial feeling without making the product difficult to use

The interface should **not** look like a generic SaaS dashboard. It should feel intentionally designed and brand-led.

### Core principles

1. **Typography is the visual hero.**
2. **Use large type and whitespace instead of decorative UI.**
3. **Use the palette in large blocks, not tiny accents everywhere.**
4. **Cards should feel like editorial tiles, not default Bootstrap cards.**
5. **Animations should be subtle and intentional.**
6. **Keep the interface highly readable and accessible.**

---

# 2. Brand Color Palette

The supplied color reference defines three primary brand colors.

| Name | HEX | RGB | Primary use |
|---|---|---|---|
| Black | `#000000` | `0, 0, 0` | Main background, headings, navigation, strong contrast |
| French Beige | `#AD7D56` | `173, 125, 86` | Primary warm accent, featured sections, selected cards |
| Rodeo Dust | `#CDB49E` | `205, 180, 158` | Soft surfaces, secondary cards, backgrounds |

### Contrast neutral

`#FFFFFF` may be used strictly as a contrast utility for text/icons on Black and dark imagery. It is **not considered a fourth brand color**.

### Recommended ratio

Use the colors approximately as:

- **Black:** 55–65%
- **Rodeo Dust:** 20–30%
- **French Beige:** 10–20%

Do not make every component beige. The strongest visual identity comes from large, confident blocks of Black with selective warm-color surfaces.

### Color behavior

#### Black `#000000`

Use for:

- Navbar
- Main hero background
- Major headings
- Primary buttons
- Footer
- Active navigation states
- High-priority card variants

#### French Beige `#AD7D56`

Use for:

- Featured cards
- Important category blocks
- Selected states
- Secondary hero panels
- Visual highlights
- Hover backgrounds on selected components

#### Rodeo Dust `#CDB49E`

Use for:

- Soft card backgrounds
- Login panel surfaces
- Supporting sections
- Secondary cards
- Form backgrounds
- Calm informational areas

---

# 3. Typography System

The second supplied reference uses a strong **modern sans-serif + elegant italic serif** pairing.

Use the following font pairing:

## Primary — Manrope

**Role:** UI, navigation, headings, body text, buttons, labels, card content.

Manrope should carry most of the interface because it is modern, geometric, highly readable, and works well for both large display type and functional UI.

### Use Manrope for

- Navbar
- Hero headline
- Hero supporting copy
- Card titles
- Card descriptions
- Buttons
- Form labels
- Inputs
- Dashboard/card metadata
- Navigation
- Error/success messages

### Recommended weights

- 400 — body
- 500 — labels
- 600 — navigation and card titles
- 700 — headings
- 800 — hero/display type

---

## Secondary — Cormorant Garamond

**Role:** Editorial emphasis and expressive words.

Cormorant Garamond should be used sparingly, preferably in italic.

### Use Cormorant Garamond for

- One emphasized word inside a hero headline
- Editorial pull quotes
- Section introductions
- Small brand statements
- Selected words such as “ideas”, “clarity”, “discover”, or “growth”
- Occasional card accent text

### Do not use Cormorant Garamond for

- Form inputs
- Navigation
- Buttons
- Dense body text
- Long descriptions
- Technical information

### Example pairing

```text
BUILD BETTER
ideas
FOR YOUR USERS
```

`BUILD BETTER` → Manrope ExtraBold

`ideas` → Cormorant Garamond Italic

This creates the same editorial contrast shown in the reference.

---

# 4. Type Scale

Use a responsive type scale.

| Element | Desktop | Tablet | Mobile |
|---|---:|---:|---:|
| Hero display | 72–96px | 56–72px | 42–52px |
| H1 | 56–72px | 48–56px | 36–44px |
| H2 | 40–52px | 36–44px | 30–36px |
| H3 | 28–34px | 26–30px | 22–26px |
| Card title | 22–28px | 20–24px | 19–22px |
| Body | 16–18px | 16px | 15–16px |
| Label | 12–14px | 12–14px | 11–13px |

### Typography rules

- Use **tight line-height** for display headings.
- Use generous line-height for body text.
- Avoid paragraphs wider than approximately 65–75 characters.
- Do not use more than two font families.
- Avoid excessive font weights.
- Let typography create hierarchy instead of adding borders and shadows everywhere.

---

# 5. Global Layout

## Page width

Use:

```css
--container-width: 1280px;
--page-padding-desktop: 48px;
--page-padding-tablet: 32px;
--page-padding-mobile: 20px;
```

Content should sit inside a centered max-width container.

## Spacing scale

Use a consistent 8px-based system:

```text
8
16
24
32
40
48
64
80
96
120
160
```

Large sections should generally have **80–160px vertical spacing** on desktop.

---

# 6. Navbar

The navbar should be minimal and editorial.

### Structure

```text
[ LOGO ]          [ Home ] [ Explore ] [ About ] [ Contact ]     [ Login ]
```

### Desktop

- Height: 72–88px
- Black background or transparent over a Black hero
- Logo aligned left
- Navigation centered/right
- Login/action aligned right
- Manrope 500–600
- Uppercase or sentence case is acceptable, but remain consistent

### Mobile

Use:

```text
[ LOGO ]                                      [ MENU ]
```

Open a full-screen or large overlay menu.

### Navbar behavior

- Transparent at the top of the hero if contrast is strong.
- Become solid Black after scrolling.
- Navigation links should have subtle underline/opacity transitions.
- Avoid heavy drop shadows.

---

# 7. Hero Section

The hero is the strongest visual statement on the homepage.

## Composition

Recommended structure:

```text
------------------------------------------------
| NAVBAR                                       |
|                                              |
|        SMALL EYEBROW                         |
|                                              |
|        MAIN HEADLINE                         |
|        with one italic serif word            |
|                                              |
|        Supporting description                |
|                                              |
|        [ PRIMARY CTA ] [ SECONDARY CTA ]     |
|                                              |
|                              VISUAL / IMAGE  |
------------------------------------------------
```

### Hero style

- Background: Black
- Main text: White
- Serif emphasis: Cormorant Garamond Italic
- Accent panel/image: French Beige or Rodeo Dust
- Minimum desktop height: 80vh
- Prefer generous whitespace
- Headline should be visually dominant

### Example hierarchy

```text
DESIGN
that makes
PRODUCTS
MEMORABLE
```

`DESIGN / PRODUCTS / MEMORABLE` → Manrope ExtraBold

`that makes` → Cormorant Garamond Italic

---

# 8. Homepage — Three Feature Cards

The homepage should contain three large editorial feature cards.

## Recommended layout

Desktop:

```text
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│                 │ │                 │ │                 │
│     CARD 01     │ │     CARD 02     │ │     CARD 03     │
│                 │ │                 │ │                 │
│  Title          │ │  Title          │ │  Title          │
│  Description    │ │  Description    │ │  Description    │
│                 │ │                 │ │                 │
│  → Explore      │ │  → Explore      │ │  → Explore      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

Mobile:

```text
CARD 01
CARD 02
CARD 03
```

Cards should stack vertically.

## Card styling

- Border radius: 0–12px
- Prefer minimal radius rather than highly rounded SaaS cards
- No default shadow
- Use strong background colors
- Use large typography
- Use asymmetric spacing
- Add subtle image/texture only when necessary

### Card variants

**Card A — Black**

- Black background
- White typography
- Strongest CTA

**Card B — French Beige**

- French Beige background
- Black typography
- Featured/creative feeling

**Card C — Rodeo Dust**

- Rodeo Dust background
- Black typography
- Supporting/informational feeling

### Hover interaction

On hover:

- Card moves up 4–8px
- Internal visual shifts slightly
- CTA arrow moves horizontally
- Background remains within the same palette
- Transition: 250–400ms

Do not use excessive scaling.

---

# 9. Card System — 27 Cards

The product contains approximately **27 cards**, so the design system must support a repeatable card architecture.

Do not create 27 completely different visual components.

Create **one core card system with variants**.

## Core card anatomy

```text
┌──────────────────────────────┐
│ CATEGORY / NUMBER            │
│                              │
│                              │
│        VISUAL / ICON         │
│                              │
│ TITLE                        │
│ Short supporting description │
│                              │
│ ACTION                 →     │
└──────────────────────────────┘
```

## Card variants

### 01 — Standard

For general content.

- Rodeo Dust
- Black text
- Medium visual area

### 02 — Featured

For important content.

- French Beige
- Larger title
- Strong CTA

### 03 — Dark

For high-priority content.

- Black
- White text
- High contrast

### 04 — Image

For image-led content.

- Full-bleed image
- Gradient/contrast overlay if necessary
- Text anchored to a corner

### 05 — Metric

For numbers or scores.

```text
92%
COMPLETE
```

Use oversized Manrope numbers.

### 06 — Category

For classification.

```text
01
CREATIVE
```

Use vertical or oversized typography.

### 07 — Action

For clickable actions.

- Minimal content
- Large arrow
- Strong hover state

---

# 10. 27-Card Grid

Use a responsive CSS grid.

Desktop:

```css
grid-template-columns: repeat(3, minmax(0, 1fr));
```

For special featured cards:

```css
grid-column: span 2;
```

Tablet:

```css
grid-template-columns: repeat(2, minmax(0, 1fr));
```

Mobile:

```css
grid-template-columns: 1fr;
```

### Suggested rhythm

Do not place all 27 cards in an identical 3 × 9 matrix.

Create editorial rhythm:

```text
Row 1:  Featured | Standard | Standard
Row 2:  Standard  | Featured | Standard
Row 3:  Standard  | Standard | Standard
Row 4:  Featured  | Standard | Standard
...
```

Every 4–6 cards, introduce a larger featured card or visual break.

---

# 11. Google Login Page

The current Google login experience should be redesigned as a **clean branded authentication page**, while retaining familiar Google sign-in behavior.

## Desktop layout

```text
---------------------------------------------------------
|                                                       |
|                                                       |
|              ┌─────────────────────────┐              |
|              │                         │              |
|              │        BRAND LOGO        │              |
|              │                         │              |
|              │    Welcome back         │              |
|              │    Short description    │              |
|              │                         │              |
|              │ [ Continue with Google ]│              |
|              │                         │              |
|              │ -------- OR --------     │              |
|              │                         │              |
|              │ Email / Username        │              |
|              │ [____________________]  │              |
|              │                         │              |
|              │ [ Continue ]            │              |
|              │                         │              |
|              │ Terms · Privacy         │              |
|              └─────────────────────────┘              |
|                                                       |
---------------------------------------------------------
```

## Authentication page style

- Background: Black
- Authentication card: Rodeo Dust
- Primary action: Black
- Text: Black
- Logo/contrast mark: White or Black depending on background
- No excessive shadows
- Card radius: 12–16px
- Max width: 440–480px
- Padding: 40–48px desktop
- Padding: 24px mobile

### Google button

Use an unmistakable Google sign-in button with:

- Official Google icon
- Clear text such as `Continue with Google`
- High contrast
- 48–52px height
- Full width

Do not recreate Google's entire login interface or impersonate Google's branding. The page is **your product's authentication experience** with Google as an authentication provider.

---

# 12. Form Design

Inputs should be minimal and premium.

### Input

```text
Label
┌──────────────────────────────────┐
│ Enter your email                 │
└──────────────────────────────────┘
```

Rules:

- Height: 48–56px
- Border: 1–2px Black at rest
- Focus: strong Black border
- Background: Rodeo Dust or contrast neutral
- No heavy shadows
- Labels should remain visible

### Buttons

Primary:

```text
[ CONTINUE  → ]
```

Secondary:

```text
[ GO BACK ]
```

Primary buttons should use Black with contrast text.

---

# 13. Buttons

## Primary

- Black background
- White text
- Manrope 600
- 48–56px height
- Slight letter spacing
- Minimal radius

## Secondary

- Transparent or Rodeo Dust background
- Black text
- Thin Black border

## Text button

Use for low-priority actions.

```text
Learn more →
```

---

# 14. Icons

Use a single icon family throughout the product.

Recommended style:

- Simple line icons
- 1.5–2px stroke
- No mixed icon styles
- Icons should support the typography rather than dominate it

Arrows are especially important for the editorial interaction language:

```text
→
↗
↓
```

---

# 15. Borders, Shadows & Radius

The reference design is flat and editorial.

### Prefer

- 1px borders
- Strong color blocks
- Flat surfaces
- Minimal shadows
- Small corner radii

### Avoid

- Huge blurred shadows
- Glassmorphism everywhere
- Excessive rounded cards
- Gradient-heavy UI
- Generic dashboard styling

Recommended:

```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
```

---

# 16. Motion & Interaction

Animation should feel **smooth and editorial**, not like a template.

### Page entrance

- Fade + small vertical movement
- 400–700ms
- Stagger cards slightly

### Card hover

```text
translateY(-4px)
```

### CTA arrow

```text
translateX(4px)
```

### Navigation

Use subtle opacity/underline transitions.

### Avoid

- Bouncy animations
- Constant floating effects
- Large rotations
- Excessive parallax

---

# 17. Responsive Behavior

## Desktop — 1200px+

Use:

- Large hero typography
- 3-column card layouts
- Large whitespace
- Asymmetric card sizing

## Tablet — 768–1199px

Use:

- 2-column cards
- Reduced hero typography
- Reduced horizontal padding
- Maintain large spacing

## Mobile — below 768px

Use:

- 1-column cards
- Compact navbar
- 42–52px hero heading
- 20px page padding
- Full-width CTAs
- Authentication card nearly full width
- Avoid horizontal scrolling

---

# 18. Accessibility

The editorial style must not compromise usability.

Requirements:

- Maintain readable contrast
- Minimum 44px touch target
- Visible keyboard focus states
- Semantic HTML
- Proper form labels
- Descriptive button text
- Do not communicate meaning through color alone
- Respect `prefers-reduced-motion`
- Use alt text for meaningful imagery

---

# 19. Component Architecture

Build reusable components rather than styling each page independently.

Recommended components:

```text
Layout
├── Navbar
├── Footer
├── Container
│
├── Hero
│
├── Typography
│   ├── DisplayHeading
│   ├── SectionHeading
│   └── EditorialAccent
│
├── Cards
│   ├── BaseCard
│   ├── FeaturedCard
│   ├── DarkCard
│   ├── ImageCard
│   ├── MetricCard
│   ├── CategoryCard
│   └── ActionCard
│
├── Forms
│   ├── Input
│   ├── Button
│   └── GoogleButton
│
└── Auth
    ├── LoginCard
    └── AuthLayout
```

---

# 20. CSS Design Tokens

Use centralized variables.

```css
:root {
  --black: #000000;
  --french-beige: #AD7D56;
  --rodeo-dust: #CDB49E;
  --white: #FFFFFF;

  --font-primary: "Manrope", sans-serif;
  --font-editorial: "Cormorant Garamond", serif;

  --container: 1280px;

  --space-1: 8px;
  --space-2: 16px;
  --space-3: 24px;
  --space-4: 32px;
  --space-5: 40px;
  --space-6: 48px;
  --space-7: 64px;
  --space-8: 80px;
  --space-9: 96px;
  --space-10: 120px;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  --transition-fast: 200ms ease;
  --transition-base: 350ms ease;
};
```

---

# 21. Google Fonts

Load only the two selected families.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<link
  href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=Manrope:wght@400;500;600;700;800&display=swap"
  rel="stylesheet"
>
```

---

# 22. Final Visual Rule

When making design decisions that are not explicitly covered in this document, follow this hierarchy:

**Typography → Space → Color → Composition → Interaction → Decoration**

Do not solve visual problems by adding more components, gradients, shadows, or decorative elements.

The final product should look like a **premium editorial brand system translated into a modern digital product**, not a generic SaaS template.
