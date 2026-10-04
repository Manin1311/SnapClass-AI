import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    is_dark = (st.session_state.get('theme_mode', 'light') == 'dark')

    if is_dark:
        bg_card = "rgba(17, 24, 39, 0.7)"
        border_card = "rgba(255, 255, 255, 0.08)"
        title_color = "#F8FAFC"
        text_sub = "#94A3B8"
        sec_color = "#E2E8F0"
        stat_bg = "rgba(255, 255, 255, 0.04)"
        stat_border = "rgba(255, 255, 255, 0.08)"
        shadow = "0 8px 24px -6px rgba(0,0,0,0.35)"
    else:
        bg_card = "#FFFFFF"
        border_card = "#E2E8F0"
        title_color = "#0F172A"
        text_sub = "#475569"
        sec_color = "#1E293B"
        stat_bg = "#F8FAFC"
        stat_border = "#E2E8F0"
        shadow = "0 4px 12px -2px rgba(0, 0, 0, 0.05)"

    stats_html = ""
    if stats:
        stats_html += """
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:14px;">
        """
        for icon, label, value in stats:
            stats_html += f"""
                <div style="background:{stat_bg}; border:1px solid {stat_border}; padding:6px 12px; border-radius:8px; font-size:0.82rem; color:{text_sub}; display:flex; align-items:center; gap:6px;">
                    <span>{icon}</span>
                    <span>{label}:</span>
                    <strong style="color:{title_color}; font-weight:700;">{value}</strong>
                </div>
            """
        stats_html += "</div>"

    html = f"""
        <div style="background:{bg_card}; border:1px solid {border_card}; padding:1.4rem; border-radius:14px; position:relative; overflow:hidden; margin-bottom:1rem; box-shadow:{shadow};">
            <div style="position:absolute; top:0; left:0; width:100%; height:3px; background:linear-gradient(90deg, #4F46E5, #38BDF8);"></div>
            <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
                <div>
                    <h3 style="margin:0 0 6px 0; color:{title_color}; font-size:1.2rem; font-weight:700; letter-spacing:-0.01em;">{name}</h3>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.82rem;">
                        <span style="background:rgba(79, 70, 229, 0.1); border:1px solid rgba(79, 70, 229, 0.25); color:#4F46E5; font-family:'JetBrains Mono', monospace; font-weight:700; padding:2px 8px; border-radius:6px;">{code}</span>
                        <span style="color:#CBD5E1;">•</span>
                        <span style="color:{text_sub};">Section <strong style="color:{sec_color};">{section}</strong></span>
                    </div>
                </div>
            </div>
            {stats_html}
        </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
