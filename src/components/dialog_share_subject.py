import streamlit as st
import segno
import io
import os


def _get_base_url():
    """Detect cloud or public deployment URL."""
    try:
        if "APP_URL" in st.secrets:
            return st.secrets["APP_URL"].rstrip("/")
    except Exception:
        pass

    app_env = os.environ.get("APP_URL")
    if app_env:
        return app_env.rstrip("/")

    try:
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers or {}
            host = headers.get("host") or headers.get("x-forwarded-host")
            if host and "localhost" not in host and "127.0.0.1" not in host:
                proto = headers.get("x-forwarded-proto", "https")
                return f"{proto}://{host}"
    except Exception:
        pass

    return "https://snapclass-biometric.streamlit.app"


@st.dialog("Class Enrollment QR & Link")
def share_subject_dialog(subject_name, subject_code):
    cloud_base = _get_base_url()

    # URL mode selector
    mode = st.radio(
        "Link Target",
        options=["🌐 Cloud URL (for Students & Mobile)", "💻 Localhost (Testing on this PC)"],
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )

    if "Localhost" in mode:
        base_url = "http://localhost:8501"
    else:
        base_url = cloud_base

    join_url = f"{base_url}/?join-code={subject_code}"

    st.markdown(
        f'<div style="margin:0.5rem 0 1rem 0;">'
        f'<h3 style="margin:0; font-size:1.2rem; color:#F8FAFC; font-weight:700;">{subject_name}</h3>'
        f'<p style="margin:4px 0 0 0; color:#94A3B8; font-size:0.83rem;">'
        f'Students can scan this QR code or use the link below to enroll instantly.'
        f'</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    qr = segno.make(join_url)
    out = io.BytesIO()
    qr.save(out, kind='png', scale=8, border=2)

    col1, col2 = st.columns([1.2, 1], vertical_alignment='center')

    with col1:
        st.markdown(
            f'<div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:12px; margin-bottom:12px;">'
            f'<div style="font-size:0.75rem; text-transform:uppercase; color:#94A3B8; font-weight:600; letter-spacing:0.5px;">Subject Enrollment Code</div>'
            f'<div style="font-size:1.4rem; font-family:\'JetBrains Mono\', monospace; font-weight:800; color:#818CF8; letter-spacing:1px; margin-top:4px;">{subject_code}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.caption("Direct Join URL:")
        st.code(join_url, language="text")

    with col2:
        st.image(out.getvalue(), caption="Scan to auto-enroll via camera", use_container_width=True)
