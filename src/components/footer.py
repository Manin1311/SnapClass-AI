import streamlit as st


def footer_home():
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')
    border_color = "rgba(255,255,255,0.06)" if is_dark else "#E2E8F0"
    text_color = "#64748B" if is_dark else "#64748B"
    sub_color = "#475569" if is_dark else "#94A3B8"

    st.markdown(f"""
        <div style="margin-top:3.5rem; padding-top:1.5rem; border-top:1px solid {border_color}; display:flex; flex-direction:column; align-items:center; gap:8px;">
            <div style="display:flex; gap:18px; font-size:0.8rem; color:{text_color}; flex-wrap:wrap; justify-content:center;">
                <span>🔒 256-bit Vector Encryption</span>
                <span>•</span>
                <span>⚡ Real-time Multi-Face Recognition</span>
                <span>•</span>
                <span>☁️ Supabase PostgreSQL Cloud</span>
            </div>
            <p style="margin:0; font-size:0.75rem; color:{sub_color};">
                SnapClass AI Campus Intelligence • Production Release
            </p>
        </div>
    """, unsafe_allow_html=True)


def footer_dashboard():
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')
    border_color = "rgba(255,255,255,0.06)" if is_dark else "#E2E8F0"
    text_color = "#64748B" if is_dark else "#64748B"

    st.markdown(f"""
        <div style="margin-top:3rem; padding-top:1rem; border-top:1px solid {border_color}; display:flex; justify-content:space-between; align-items:center; font-size:0.78rem; color:{text_color};">
            <span>SnapClass AI • Biometric Attendance Platform</span>
            <span>Cloud Status: <strong style="color:#10B981;">Operational</strong></span>
        </div>
    """, unsafe_allow_html=True)
