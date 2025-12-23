"""
GPTBuddyAI - Nordic Design Theme
Minimalist color palette: greys and blues
"""

# Nordic Color Palette
COLORS = {
    # Greys
    'background': '#F5F5F5',      # Light grey background
    'surface': '#FFFFFF',          # White cards/surfaces
    'border': '#E0E0E0',          # Medium grey borders
    'text_primary': '#2E3440',    # Dark grey text (Nordic dark)
    'text_secondary': '#4C566A',  # Medium grey text
    'text_tertiary': '#D8DEE9',   # Light grey text

    # Blues (Primary brand colors)
    'primary': '#4A90E2',         # Bright blue (accent)
    'primary_dark': '#2E5C8A',    # Deep blue (headers)
    'primary_light': '#7AB8F5',   # Light blue (hover states)

    # Semantic colors
    'success': '#A3BE8C',         # Nordic green
    'warning': '#EBCB8B',         # Nordic yellow
    'error': '#BF616A',           # Nordic red
    'info': '#5E81AC',            # Nordic frost blue
}

# Typography
FONTS = {
    'primary': '"Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    'monospace': '"SF Mono", "Fira Code", "Consolas", monospace',
}

# Streamlit Custom CSS
STREAMLIT_CSS = f"""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global theme */
    :root {{
        --background: {COLORS['background']};
        --surface: {COLORS['surface']};
        --primary: {COLORS['primary']};
        --primary-dark: {COLORS['primary_dark']};
        --text-primary: {COLORS['text_primary']};
    }}

    /* Main container */
    .main {{
        background-color: {COLORS['background']};
        font-family: {FONTS['primary']};
    }}

    /* Headers */
    h1 {{
        color: {COLORS['primary_dark']};
        font-weight: 600;
        letter-spacing: -0.02em;
        margin-bottom: 1.5rem;
    }}

    h2 {{
        color: {COLORS['primary_dark']};
        font-weight: 500;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }}

    h3 {{
        color: {COLORS['text_primary']};
        font-weight: 500;
        font-size: 1.1rem;
    }}

    /* Cards and surfaces */
    .stMarkdown, .element-container {{
        background-color: {COLORS['surface']};
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['surface']};
        border-right: 1px solid {COLORS['border']};
    }}

    [data-testid="stSidebar"] h1 {{
        color: {COLORS['primary_dark']};
        font-size: 1.5rem;
        font-weight: 600;
    }}

    /* Buttons */
    .stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }}

    .stButton > button:hover {{
        background-color: {COLORS['primary_dark']};
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        transform: translateY(-1px);
    }}

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 0.75rem;
        font-family: {FONTS['primary']};
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['primary']};
        box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
    }}

    /* Sliders */
    .stSlider > div > div > div > div {{
        background-color: {COLORS['primary']};
    }}

    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {COLORS['primary_dark']};
        font-weight: 600;
    }}

    /* Charts */
    .vega-embed {{
        background-color: {COLORS['surface']};
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }}

    /* Expandable sections */
    .streamlit-expanderHeader {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        color: {COLORS['text_primary']};
        font-weight: 500;
    }}

    .streamlit-expanderHeader:hover {{
        border-color: {COLORS['primary']};
    }}

    /* Code blocks */
    code {{
        background-color: {COLORS['background']};
        color: {COLORS['primary_dark']};
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: {FONTS['monospace']};
        font-size: 0.9em;
    }}

    pre {{
        background-color: {COLORS['background']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 1rem;
    }}

    /* Tables */
    table {{
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid {COLORS['border']};
    }}

    thead tr {{
        background-color: {COLORS['primary_dark']};
        color: white;
    }}

    tbody tr:hover {{
        background-color: {COLORS['background']};
    }}

    /* Logo container */
    .logo-container {{
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }}

    .logo-container img {{
        width: 48px;
        height: 48px;
    }}

    .logo-container h1 {{
        margin: 0;
        font-size: 1.8rem;
    }}

    /* Smooth transitions */
    * {{
        transition: background-color 0.2s ease, border-color 0.2s ease;
    }}

    /* Scrollbar styling */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: {COLORS['background']};
    }}

    ::-webkit-scrollbar-thumb {{
        background: {COLORS['border']};
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['text_secondary']};
    }}
</style>
"""

# Altair/Vega chart theme
CHART_THEME = {
    'config': {
        'view': {
            'strokeWidth': 0,
            'height': 300,
            'width': 400,
        },
        'background': COLORS['surface'],
        'axis': {
            'labelColor': COLORS['text_secondary'],
            'titleColor': COLORS['text_primary'],
            'gridColor': COLORS['border'],
            'domainColor': COLORS['border'],
            'tickColor': COLORS['border'],
            'labelFont': 'Inter, sans-serif',
            'titleFont': 'Inter, sans-serif',
            'labelFontSize': 11,
            'titleFontSize': 13,
            'titleFontWeight': 500,
        },
        'header': {
            'labelColor': COLORS['text_primary'],
            'titleColor': COLORS['text_primary'],
            'labelFont': 'Inter, sans-serif',
            'titleFont': 'Inter, sans-serif',
        },
        'legend': {
            'labelColor': COLORS['text_secondary'],
            'titleColor': COLORS['text_primary'],
            'labelFont': 'Inter, sans-serif',
            'titleFont': 'Inter, sans-serif',
            'labelFontSize': 11,
            'titleFontSize': 12,
        },
        'mark': {
            'color': COLORS['primary'],
        },
        'line': {
            'color': COLORS['primary'],
            'strokeWidth': 2,
        },
        'bar': {
            'color': COLORS['primary'],
        },
        'point': {
            'color': COLORS['primary'],
            'filled': True,
        },
        'area': {
            'color': COLORS['primary'],
            'opacity': 0.7,
        },
        'title': {
            'color': COLORS['text_primary'],
            'fontSize': 16,
            'fontWeight': 600,
            'font': 'Inter, sans-serif',
            'anchor': 'start',
        },
    }
}
