import streamlit as st


def render_theme_toggle(compact=False, key="theme_toggle_btn"):
    """Render the theme toggle button.
    compact=True → icon-only (🌙/☀️) for tight spaces like the top-right bar.
    compact=False → full label for home screen top bar.
    """
    current = st.session_state.get('theme_mode', 'light')
    target = 'dark' if current == 'light' else 'light'
    if compact:
        label = "🌙" if current == 'light' else "☀️"
    else:
        label = "🌙 Dark Mode" if current == 'light' else "☀️ Light Mode"
    if st.button(label, key=key, type="secondary", help="Toggle Light / Dark Mode"):
        st.session_state['theme_mode'] = target
        st.rerun()


def header_home():
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')

    badge_bg = "rgba(99, 102, 241, 0.12)" if is_dark else "#EEF2FF"
    badge_border = "rgba(99, 102, 241, 0.3)" if is_dark else "#C7D2FE"
    badge_text = "#A5B4FC" if is_dark else "#4338CA"

    title_color = "#FFFFFF" if is_dark else "#0F172A"
    ai_accent_color = "#818CF8" if is_dark else "#4F46E5"
    subtitle_color = "#94A3B8" if is_dark else "#475569"

    # Top Bar with Theme Toggle
    top_col1, top_col2 = st.columns([5, 1], vertical_alignment='center')
    with top_col2:
        render_theme_toggle(compact=False, key="theme_toggle_home")

    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-top:0.5rem; margin-bottom:2.25rem; text-align:center;">
            <div style="display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:30px; background:{badge_bg}; border:1px solid {badge_border}; margin-bottom:1rem;">
                <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981; box-shadow:0 0 8px #10B981;"></span>
                <span style="font-size:0.75rem; font-weight:700; color:{badge_text}; letter-spacing:0.5px; text-transform:uppercase;">Campus Biometric Intelligence v2.4</span>
            </div>
            <h1 style="margin:0; font-size:2.8rem; font-weight:800; color:{title_color}; letter-spacing:-0.03em;">
                SnapClass <span style="color:{ai_accent_color};">AI</span>
            </h1>
            <p style="margin-top:0.5rem; font-size:1.02rem; color:{subtitle_color}; max-width:560px; font-weight:400; line-height:1.5;">
                Enterprise-grade facial & voice biometric attendance automation with multi-student instant recognition.
            </p>
        </div>
    """, unsafe_allow_html=True)


def header_dashboard():
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')
    title_color = "#F8FAFC" if is_dark else "#0F172A"
    sub_color = "#64748B" if is_dark else "#64748B"

    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; padding:0.25rem 0;">
            <div style="display:flex; align-items:center; justify-content:center; width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); box-shadow:0 4px 12px rgba(79, 70, 229, 0.35);">
                <span style="font-size:1.2rem; color:white;">⚡</span>
            </div>
            <div>
                <h3 style="margin:0; font-size:1.25rem; font-weight:700; color:{title_color}; letter-spacing:-0.02em;">
                    SnapClass <span style="color:#4F46E5;">AI</span>
                </h3>
                <p style="margin:0; font-size:0.75rem; color:{sub_color}; font-weight:500;">
                    Enterprise Biometric Suite
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
