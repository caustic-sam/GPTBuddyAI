# GPTBuddyAI - Branding Assets

## Logo

**File**: `logo.svg`

**Design**: Minimalist Nordic-style songbird silhouette
- **Colors**: Blue gradient (#4A90E2 → #2E5C8A)
- **Style**: Clean, geometric, single continuous path
- **Format**: Scalable SVG (100x100 viewBox)

### Usage
```python
# In Streamlit
st.image("src/ui/assets/logo.svg", width=48)

# Or as base64 embedded in HTML
with open("src/ui/assets/logo.svg") as f:
    logo_svg = f.read()
st.markdown(f'<div class="logo-container">{logo_svg}<h1>GPTBuddyAI</h1></div>', unsafe_allow_html=True)
```

---

## Color Palette

### Nordic Greys
- **Background**: `#F5F5F5` - Light grey for app background
- **Surface**: `#FFFFFF` - White for cards and content areas
- **Border**: `#E0E0E0` - Medium grey for subtle borders
- **Text Primary**: `#2E3440` - Dark grey for main text
- **Text Secondary**: `#4C566A` - Medium grey for secondary text

### Nordic Blues (Brand Colors)
- **Primary**: `#4A90E2` - Bright blue for CTAs and accents
- **Primary Dark**: `#2E5C8A` - Deep blue for headers and emphasis
- **Primary Light**: `#7AB8F5` - Light blue for hover states

### Semantic Colors
- **Success**: `#A3BE8C` - Nordic green
- **Warning**: `#EBCB8B` - Nordic yellow
- **Error**: `#BF616A` - Nordic red
- **Info**: `#5E81AC` - Nordic frost blue

---

## Typography

### Font Families
- **Primary**: Inter (Google Fonts) - Clean, modern sans-serif
- **Fallback**: SF Pro Display, -apple-system, system-ui
- **Monospace**: SF Mono, Fira Code, Consolas

### Font Weights
- **Light**: 300 - Body text (optional)
- **Regular**: 400 - Default body text
- **Medium**: 500 - Subheadings, buttons
- **Semibold**: 600 - Headings, emphasis
- **Bold**: 700 - Strong emphasis (rare)

---

## Design Principles

1. **Minimalism**: Remove unnecessary elements, embrace whitespace
2. **Clarity**: Prioritize readability and intuitive navigation
3. **Consistency**: Use color palette and typography consistently
4. **Depth**: Subtle shadows and borders for visual hierarchy
5. **Smoothness**: Gentle transitions and hover effects

---

## Implementation

All styling is centralized in `src/ui/theme.py`:
- `COLORS` dict for color palette
- `FONTS` dict for typography
- `STREAMLIT_CSS` for custom Streamlit styling
- `CHART_THEME` for Altair/Vega chart styling

Import and use in Streamlit apps:
```python
from theme import STREAMLIT_CSS, COLORS, CHART_THEME

st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)
```

---

_Created: Dec 21, 2025_
_Style: Nordic Minimalist_
