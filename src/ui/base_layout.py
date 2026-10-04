import streamlit as st


def get_current_theme():
    if 'theme_mode' not in st.session_state:
        st.session_state['theme_mode'] = 'light'  # Default to clean Light Mode as requested
    return st.session_state['theme_mode']


def style_base_layout():
    """
    Production-Grade Dual Theme Design System (Light Mode by default, Dark Mode support).
    Fixes input overlap issues, constrains biometric camera viewfinder, and applies
    modern Plus Jakarta Sans & Inter typography.
    """
    theme = get_current_theme()
    is_dark = (theme == 'dark')

    if is_dark:
        bg_app = "#0B0F19"
        bg_card = "rgba(17, 24, 39, 0.75)"
        bg_card_inner = "rgba(30, 41, 59, 0.5)"
        border_card = "rgba(255, 255, 255, 0.08)"
        text_primary = "#F8FAFC"
        text_secondary = "#94A3B8"
        text_muted = "#64748B"
        input_bg = "rgba(15, 23, 42, 0.85)"
        input_border = "rgba(255, 255, 255, 0.12)"
        btn_pri_bg = "linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)"
        btn_pri_text = "#FFFFFF"
        btn_pri_border = "transparent"
        btn_sec_bg = "rgba(30, 41, 59, 0.8)"
        btn_sec_text = "#E2E8F0"
        btn_sec_border = "rgba(255, 255, 255, 0.1)"
        kpi_bg = "rgba(17, 24, 39, 0.7)"
        card_shadow = "0 10px 25px -5px rgba(0, 0, 0, 0.5)"
    else:
        # Crisp, Clean Enterprise Light Theme (Preferable for Faculty & Presentations)
        bg_app = "#F8FAFC"
        bg_card = "#FFFFFF"
        bg_card_inner = "#F1F5F9"
        border_card = "#E2E8F0"
        text_primary = "#0F172A"
        text_secondary = "#475569"
        text_muted = "#94A3B8"
        input_bg = "#FFFFFF"
        input_border = "#CBD5E1"
        btn_pri_bg = "#EEF2FF"
        btn_pri_text = "#3730A3"
        btn_pri_border = "#C7D2FE"
        btn_sec_bg = "#F1F5F9"
        btn_sec_text = "#1E293B"
        btn_sec_border = "#CBD5E1"
        kpi_bg = "#FFFFFF"
        card_shadow = "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05), 0 16px 24px -4px rgba(0, 0, 0, 0.04)"

    css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Hide Streamlit Default Chrome & Cloud Viewer Badges */
        #MainMenu, footer, header,
        [data-testid="stToolbar"],
        [data-testid="stHeader"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [class*="viewerBadge"],
        [class*="manageApp"],
        #manage-app-button,
        [data-testid="manage-app-button"],
        .stDeployButton,
        [class*="FloatingMenu"] {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
            pointer-events: none !important;
        }}

        /* CRITICAL FIX: Hide all "Press Enter to apply" popups that overlap inputs */
        div[data-testid*="nputInstructions"],
        div[data-testid*="instructions"],
        div[data-testid*="Instruction"],
        div[data-testid="stInputInstructions"],
        .stTextInput small, 
        .stPasswordInput small,
        div[data-baseweb="base-input"] + div,
        div[data-baseweb="input"] + div {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            pointer-events: none !important;
            position: absolute !important;
        }}

        /* Canvas */
        .stApp {{
            background-color: {bg_app} !important;
            color: {text_primary} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}

        .block-container {{
            max-width: 1160px !important;
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }}

        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            color: {text_primary} !important;
            letter-spacing: -0.025em !important;
            font-weight: 700 !important;
        }}

        p, label, .stMarkdown p {{
            font-family: 'Inter', sans-serif !important;
            color: {text_secondary} !important;
        }}

        /* Protect Material Icons / Font Glyphs from font override */
        .material-symbols-rounded,
        .material-symbols-outlined,
        .material-icons,
        [class*="material-symbols"],
        [class*="material-icons"],
        .stPasswordInput button *,
        div[data-baseweb="input"] button * {{
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
            font-size: 1.25rem !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
        }}

        /* Streamlit Bordered Containers (Glass Cards) */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background: {bg_card} !important;
            border: 1px solid {border_card} !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            box-shadow: {card_shadow} !important;
        }}

        /* Modern Action Buttons base styles */
        .stButton > button,
        button[kind="primary"],
        button[kind="secondary"] {{
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            font-size: 0.93rem !important;
            border-radius: 10px !important;
            padding: 0.65rem 1.4rem !important;
            letter-spacing: 0.01em !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}

        /* Primary Button */
        button[kind="primary"],
        .stButton > button[kind="primary"] {{
            background: {btn_pri_bg} !important;
            color: {btn_pri_text} !important;
            border: 1.5px solid {btn_pri_border} !important;
            box-shadow: 0 2px 8px rgba(79, 70, 229, 0.12) !important;
        }}

        button[kind="primary"] p,
        button[kind="primary"] span,
        button[kind="primary"] div,
        .stButton > button[kind="primary"] p,
        .stButton > button[kind="primary"] span {{
            color: {btn_pri_text} !important;
            font-weight: 700 !important;
        }}

        button[kind="primary"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 16px rgba(79, 70, 229, 0.22) !important;
            filter: brightness(0.97) !important;
        }}

        /* Secondary Button */
        button[kind="secondary"],
        .stButton > button[kind="secondary"] {{
            background: {btn_sec_bg} !important;
            color: {btn_sec_text} !important;
            border: 1.5px solid {btn_sec_border} !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
        }}

        button[kind="secondary"] p,
        button[kind="secondary"] span,
        .stButton > button[kind="secondary"] p,
        .stButton > button[kind="secondary"] span {{
            color: {btn_sec_text} !important;
            font-weight: 700 !important;
        }}

        button[kind="secondary"]:hover {{
            background: {bg_card_inner} !important;
            border-color: #818CF8 !important;
            transform: translateY(-1px) !important;
        }}

        /* Password Visibility Toggle Button Reset (Keeps eye icon clean, compact and transparent) */
        .stPasswordInput button,
        div[data-baseweb="input"] button,
        div[data-baseweb="base-input"] button {{
            all: unset !important;
            cursor: pointer !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: transparent !important;
            border: none !important;
            padding: 4px 8px !important;
            margin: 0 !important;
            width: auto !important;
            height: auto !important;
            color: {text_secondary} !important;
            box-shadow: none !important;
            transform: none !important;
        }}

        .stPasswordInput button:hover,
        div[data-baseweb="input"] button:hover {{
            background: transparent !important;
            color: #4F46E5 !important;
            box-shadow: none !important;
            transform: none !important;
        }}

        /* Form Inputs */
        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        .stTextInput input,
        .stPasswordInput input {{
            background-color: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 10px !important;
            color: {text_primary} !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.95rem !important;
            height: 44px !important;
        }}

        div[data-baseweb="input"]:focus-within,
        .stTextInput input:focus,
        .stPasswordInput input:focus {{
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18) !important;
        }}

        /* CRITICAL FIX: Constrain Camera Input Size so it doesn't take over screen */
        div[data-testid="stCameraInput"] {{
            max-width: 500px !important;
            margin: 0 auto 1.5rem auto !important;
            border: 2px dashed rgba(99, 102, 241, 0.4) !important;
            border-radius: 18px !important;
            padding: 12px !important;
            background: {bg_card} !important;
            box-shadow: {card_shadow} !important;
        }}

        div[data-testid="stCameraInput"] video {{
            border-radius: 12px !important;
        }}

        /* Always show "Take Photo" button — Streamlit hides it until hover by default */
        div[data-testid="stCameraInput"] button {{
            opacity: 1 !important;
            visibility: visible !important;
            display: flex !important;
            pointer-events: auto !important;
            background: rgba(79, 70, 229, 0.85) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
            letter-spacing: 0.02em !important;
            transition: background 0.2s ease !important;
        }}

        div[data-testid="stCameraInput"] button:hover {{
            background: #4F46E5 !important;
            color: #FFFFFF !important;
        }}

        div[data-testid="stCameraInput"] button p,
        div[data-testid="stCameraInput"] button span {{
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }}


        /* Selectboxes */
        div[data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 10px !important;
            color: {text_primary} !important;
        }}

        /* DataFrames */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {border_card} !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: {card_shadow} !important;
        }}

        hr {{
            border-color: {border_card} !important;
            margin: 1.5rem 0 !important;
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def style_background_home():
    style_base_layout()


def style_background_dashboard():
    style_base_layout()