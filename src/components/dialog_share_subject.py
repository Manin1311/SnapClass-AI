import streamlit as st
import segno
import io


@st.dialog("Class Enrollment QR & Link")
def share_subject_dialog(subject_name, subject_code):
    join_url = f"http://localhost:8501/?join-code={subject_code}"

    st.markdown(f"""
        <div style="margin-bottom:1rem;">
            <h3 style="margin:0; font-size:1.25rem; color:#F8FAFC;">{subject_name}</h3>
            <p style="margin:2px 0 0 0; color:#94A3B8; font-size:0.85rem;">Share this QR code or Subject Code with your students for instant enrollment.</p>
        </div>
    """, unsafe_allow_html=True)

    qr = segno.make(join_url)
    out = io.BytesIO()
    qr.save(out, kind='png', scale=8, border=2)

    col1, col2 = st.columns([1.2, 1], vertical_alignment='center')

    with col1:
        st.markdown("""
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:12px; margin-bottom:10px;">
                <div style="font-size:0.75rem; text-transform:uppercase; color:#94A3B8; font-weight:600;">Subject Enrollment Code</div>
                <div style="font-size:1.4rem; font-family:'JetBrains Mono', monospace; font-weight:800; color:#818CF8; letter-spacing:1px; margin-top:4px;">
        """ + subject_code + """
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.caption("Direct Join URL:")
        st.code(join_url, language="text")

    with col2:
        st.image(out.getvalue(), caption="Scan to auto-enroll via camera", use_container_width=True)
