import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_background_home


def home_screen():
    style_background_home()
    header_home()

    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')

    if is_dark:
        card_bg = "rgba(17, 24, 39, 0.75)"
        card_border = "rgba(255, 255, 255, 0.08)"
        card_shadow = "0 10px 25px -5px rgba(0,0,0,0.4)"
        title_color = "#F8FAFC"
        text_color = "#94A3B8"
        chip_bg = "rgba(255,255,255,0.05)"
        chip_border = "rgba(255,255,255,0.08)"
        chip_text = "#CBD5E1"
        stats_bg = "rgba(15, 23, 42, 0.5)"
        stats_border = "rgba(255,255,255,0.08)"
    else:
        card_bg = "#FFFFFF"
        card_border = "#E2E8F0"
        card_shadow = "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 16px 24px -4px rgba(0, 0, 0, 0.04)"
        title_color = "#0F172A"
        text_color = "#475569"
        chip_bg = "#F8FAFC"
        chip_border = "#E2E8F0"
        chip_text = "#334155"
        stats_bg = "#FFFFFF"
        stats_border = "#E2E8F0"

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(f"""
            <div style="background:{card_bg}; backdrop-filter:blur(16px); border:1px solid {card_border}; border-radius:18px; padding:2rem; min-height:360px; display:flex; flex-direction:column; justify-content:space-between; position:relative; overflow:hidden; box-shadow:{card_shadow};">
                <div style="position:absolute; top:0; left:0; width:100%; height:4px; background:linear-gradient(90deg, #4F46E5, #6366F1);"></div>
                <div>
                    <div style="display:inline-flex; align-items:center; justify-content:center; width:52px; height:52px; border-radius:14px; background:rgba(79, 70, 229, 0.1); border:1px solid rgba(79, 70, 229, 0.25); margin-bottom:1.25rem;">
                        <span style="font-size:1.6rem;">🎓</span>
                    </div>
                    <div style="font-size:0.75rem; text-transform:uppercase; font-weight:700; color:#4F46E5; letter-spacing:1px; margin-bottom:4px;">
                        FACULTY SUITE
                    </div>
                    <h2 style="margin:0 0 0.6rem 0; font-size:1.65rem; color:{title_color};">
                        Faculty Portal
                    </h2>
                    <p style="color:{text_color}; font-size:0.92rem; line-height:1.5; margin-bottom:1.2rem;">
                        Automate classroom roll calls with single-click AI batch face recognition, voice verification, and exportable CSV reports.
                    </p>
                    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:1.5rem;">
                        <span style="background:{chip_bg}; border:1px solid {chip_border}; padding:4px 10px; border-radius:8px; font-size:0.78rem; color:{chip_text}; font-weight:500;">📸 Multi-Face Scan</span>
                        <span style="background:{chip_bg}; border:1px solid {chip_border}; padding:4px 10px; border-radius:8px; font-size:0.78rem; color:{chip_text}; font-weight:500;">🎙️ Voice Biometrics</span>
                        <span style="background:{chip_bg}; border:1px solid {chip_border}; padding:4px 10px; border-radius:8px; font-size:0.78rem; color:{chip_text}; font-weight:500;">📊 Export Records</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button('Access Faculty Portal →', type='primary', width='stretch', key='btn_faculty'):
            st.session_state['login_type'] = 'teacher'
            st.rerun()

    with col2:
        st.markdown(f"""
            <div style="background:{card_bg}; backdrop-filter:blur(16px); border:1px solid {card_border}; border-radius:18px; padding:2rem; min-height:360px; display:flex; flex-direction:column; justify-content:space-between; position:relative; overflow:hidden; box-shadow:{card_shadow};">
                <div style="position:absolute; top:0; left:0; width:100%; height:4px; background:linear-gradient(90deg, #10B981, #059669);"></div>
                <div>
                    <div style="display:inline-flex; align-items:center; justify-content:center; width:52px; height:52px; border-radius:14px; background:rgba(16, 185, 129, 0.1); border:1px solid rgba(16, 185, 129, 0.25); margin-bottom:1.25rem;">
                        <span style="font-size:1.6rem;">👤</span>
                    </div>
                    <div style="font-size:0.75rem; text-transform:uppercase; font-weight:700; color:#059669; letter-spacing:1px; margin-bottom:4px;">
                        STUDENT GATEWAY
                    </div>
                    <h2 style="margin:0 0 0.6rem 0; font-size:1.65rem; color:{title_color};">
                        Student Portal
                    </h2>
                    <p style="color:{text_color}; font-size:0.92rem; line-height:1.5; margin-bottom:1.2rem;">
                        Passwordless biometric sign-in using facial recognition. Track subject-wise attendance percentages and 75% eligibility.
                    </p>
                    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:1.5rem;">
                        <span style="background:{chip_bg}; border:1px solid {chip_border}; padding:4px 10px; border-radius:8px; font-size:0.78rem; color:{chip_text}; font-weight:500;">⚡ FaceID Login</span>
                        <span style="background:{chip_bg}; border:1px solid {chip_border}; padding:4px 10px; border-radius:8px; font-size:0.78rem; color:{chip_text}; font-weight:500;">📈 75% Tracker</span>
                        <span style="background:{chip_bg}; border:1px solid {chip_border}; padding:4px 10px; border-radius:8px; font-size:0.78rem; color:{chip_text}; font-weight:500;">📲 Quick QR Join</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button('Access Student Portal →', type='secondary', width='stretch', key='btn_student'):
            st.session_state['login_type'] = 'student'
            st.rerun()

    # Feature Highlights Row
    st.markdown(f"""
        <div style="margin-top:2.5rem; padding:1.25rem 1.5rem; background:{stats_bg}; border:1px solid {stats_border}; border-radius:14px; display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:1.25rem; text-align:center; box-shadow:{card_shadow};">
            <div>
                <div style="font-size:1.45rem; font-weight:800; color:{title_color}; font-family:'Plus Jakarta Sans';">99.4%</div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">Face Match Precision</div>
            </div>
            <div>
                <div style="font-size:1.45rem; font-weight:800; color:#4F46E5; font-family:'Plus Jakarta Sans';">&lt; 1.2s</div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">Inference Latency</div>
            </div>
            <div>
                <div style="font-size:1.45rem; font-weight:800; color:#10B981; font-family:'Plus Jakarta Sans';">Dual AI</div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">Vision + Voice Biometrics</div>
            </div>
            <div>
                <div style="font-size:1.45rem; font-weight:800; color:#F59E0B; font-family:'Plus Jakarta Sans';">Zero Raw</div>
                <div style="font-size:0.78rem; color:#64748B; margin-top:2px;">128-d Vector Embeddings</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    footer_home()